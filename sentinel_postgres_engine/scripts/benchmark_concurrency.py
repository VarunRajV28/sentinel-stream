import asyncio
import time
import sys
import httpx

# Native Python Concurrency Benchmark Tool
# Simulates the behavior of 'ab' using async HTTP requests

async def tick(client, url):
    try:
        resp = await client.post(url)
        return resp.status_code == 200
    except Exception:
        return False

async def run_benchmark(url, total_requests, concurrency):
    print(f"Benchmarking {url}")
    print(f"Total requests: {total_requests}, Concurrency: {concurrency}")
    
    start_time = time.perf_counter()
    success_count = 0
    
    async with httpx.AsyncClient(timeout=10) as client:
        # Process in batches to maintain concurrency level
        for i in range(0, total_requests, concurrency):
            batch_size = min(concurrency, total_requests - i)
            tasks = [tick(client, url) for _ in range(batch_size)]
            results = await asyncio.gather(*tasks)
            success_count += sum(1 for r in results if r)
            
            if (i + batch_size) % (concurrency * 5) == 0:
                print(f"Progress: {i + batch_size}/{total_requests} requests...")

    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print("\nBenchmark Results:")
    print(f"Total Time:      {duration:.2f} seconds")
    print(f"Successful:      {success_count}")
    print(f"Failed:          {total_requests - success_count}")
    print(f"Requests/sec:    {total_requests / duration:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        url = "http://localhost:8001/api/analytics/device/stress_device/velocity-tick"
    else:
        url = sys.argv[1]
        
    asyncio.run(run_benchmark(url, total_requests=1000, concurrency=50))
