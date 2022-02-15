# KEEN Smart Sensor
KEEN Smart sensor is a mtp-capable, camera-based soft sensor that enables in-field live AI-supported data analytics including data collection and model inference. The soft sensor is based on the service specification developed in cooperation of Merck, TUDo and TUD within the project KEEN.

## Requirements
To run the soft sensor third-party packages are required. To install them use the following command:
```bash
pip install -r requirements.txt
```
The smart sensor expects to have a KEEN smart camera running. Its RestAPI endpoint should be specified in main.py. By default it is assumed that both Smart Sensor and Smart Camera instances run under the same ip address.

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
