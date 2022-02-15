# KEEN Smart Sensor
KEEN Smart sensor is a mtp-capable, camera-based soft sensor that enables in-field live AI-supported data analytics including data collection and model inference. The soft sensor is based on the service specification developed in cooperation of Merck, TUDo and TUD within the project KEEN.

## Requirements
To run the soft sensor third-party packages are required. To install them use the following command:
```bash
pip install -r requirements.txt
```

## Usage
To run the soft sensor simply execute the main code from the folder /src:
```python
python main.py
```
To generate the MTP file please run the script from the folder /src:
```python
python mtp-generate.py
```
The MTP file will be generated as aml manifest and saved in the folder /mtp

## License
MIT License

Copyright (c) 2022, Technische Universität Dresden, Valentin Khaydarov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
