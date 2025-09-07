using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace AipPackageJob
{
    class Program
    {
        static async Task Main(string[] args)
        {
            string baseUrl = Environment.GetEnvironmentVariable("LIFETIME_URL") ?? "https://your-lifetime-api";
            string token = Environment.GetEnvironmentVariable("LIFETIME_TOKEN") ?? "YOUR_TOKEN";
            string envKey = Environment.GetEnvironmentVariable("ENVIRONMENT_KEY") ?? "your-env-key";
            string appKey = Environment.GetEnvironmentVariable("APPLICATION_KEY") ?? "your-app-key";
            string outputPath = Environment.GetEnvironmentVariable("OUTPUT_ZIP") ?? "app_source.zip";

            using var http = new HttpClient();
            http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            // Step 3: request package
            var packageRequestUrl = $"{baseUrl}/lifetimeapi/rest/v2/environments/{envKey}/applications/{appKey}/self/package";
            using var requestResponse = await http.PostAsync(packageRequestUrl, new StringContent("{}", System.Text.Encoding.UTF8, "application/json"));
            requestResponse.EnsureSuccessStatusCode();

            using var packageRequestStream = await requestResponse.Content.ReadAsStreamAsync();
            var packageRequestJson = await JsonDocument.ParseAsync(packageRequestStream);
            string requestKey = packageRequestJson.RootElement.GetProperty("RequestKey").GetString()!;
            Console.WriteLine($"Request key: {requestKey}");

            // Step 4: poll status
            string statusUrl = $"{packageRequestUrl}/{requestKey}";
            for (int i = 0; i < 60; i++)
            {
                using var statusResponse = await http.GetAsync(statusUrl);
                statusResponse.EnsureSuccessStatusCode();
                using var statusStream = await statusResponse.Content.ReadAsStreamAsync();
                var statusJson = await JsonDocument.ParseAsync(statusStream);
                string status = statusJson.RootElement.GetProperty("Status").GetString()!;
                if (status.Equals("Ready", StringComparison.OrdinalIgnoreCase))
                {
                    if (statusJson.RootElement.TryGetProperty("DownloadURL", out var urlElement))
                    {
                        var downloadUrl = urlElement.GetString();
                        await DownloadFileAsync(http, downloadUrl!, outputPath);
                    }
                    else if (statusJson.RootElement.TryGetProperty("DownloadKey", out var keyElement))
                    {
                        var downloadKey = keyElement.GetString();
                        var downloadUrl = $"{baseUrl}/lifetimeapi/rest/v2/download/{downloadKey}";
                        await DownloadFileAsync(http, downloadUrl, outputPath);
                    }
                    Console.WriteLine("Download complete.");
                    return;
                }
                await Task.Delay(TimeSpan.FromSeconds(5));
            }
            Console.WriteLine("Timed out waiting for package to be ready.");
        }

        static async Task DownloadFileAsync(HttpClient http, string url, string path)
        {
            using var response = await http.GetAsync(url);
            response.EnsureSuccessStatusCode();
            await using var fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None);
            await response.Content.CopyToAsync(fs);
        }
    }
}
