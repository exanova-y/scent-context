### Nonhumanscent: graphs

1. Flash `firmware/src/main.cpp` to microcontroller. You could get the vscode extension of Platformio, open `main.cpp` and simply click the arrow buttons.
2. Record data for each scent. Here the scents were recorded only 5 mins at a time.
3. Manually copy paste the data from the serial monitor into a text file inside app/data.
4. Set up the venv:
```bash
uv venv

activate the environment:
.venv\Scripts\activate (on windows) 
source .venv/bin/activate (on mac)

uv pip install -r requirements.txt
```
5. Convert some copy-pasted data into csv
```bash
python data/convert_to_csv.py
```

5. Run the test_plotting.py script:
```bash
python test_plotting.py
```


