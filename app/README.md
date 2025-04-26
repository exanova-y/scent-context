### Scent context app

Folders:
1. data-collection
2. dashboard
3. classification
4. retrieval

## How to contribute
### Recording data
1. Navigate to the firmware repo from `https://github.com/eigenlucy/nonhumanscent/`
2. Flash `firmware/src/main.cpp` to microcontroller. You could get the vscode extension of Platformio, open `main.cpp` and simply click the arrow buttons.
3. Record data for each scent. We have 30 min and 5 min recordings.
4. Manually copy paste the data from the serial monitor into a text file inside app/data-collection.

### Working on dashboard, classification and retrieval
1. Set up the venv:
```bash
uv venv

activate the environment:
.venv\Scripts\activate (on windows) 
source .venv/bin/activate (on mac)

uv pip install -r requirements.txt
```
2. Convert some txt data into csv
```bash
cd data-collection
python convert_to_csv.py
```

3. Run the test_plotting.py script:
```bash
python test_plotting.py
```


