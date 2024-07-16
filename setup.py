import time
from pathlib import Path

start = time.time() 

Path("data/cache").mkdir(parents=True, exist_ok=True)
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/transformed").mkdir(parents=True, exist_ok=True)
 
end = time.time() 
print("\nExecution time: ",end - start)