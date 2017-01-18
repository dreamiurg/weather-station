I am developing a weekend project - mini weather station, trying new technologies along the way. Weather station is running on CHIP (a $9 step brother of Raspberry Pi - check out getchip.com) reads temperature from 1-Wire DS18B20 sensor every 30 seconds and sends it to AWS IoT over MQTT, where rule is configured to save temperature in the DynamoDB.

Frontend is going to be implemented on HTML5 + React.JS. It would request last temperature from serverless backend running on API Gateway + several Labmda functions. 

# What's done
- Weather station code is complete
- AWS IoT rule set up, data is stored in DynamoDB
- Deployment process is set up using serverless 
- One API - `get_latest_weather()` is implemented

# What's left
- Create frontend to show latest temp; figure out the best way to deploy it to S3
- Set up S3/CloudFront
- Configure custom domain
- Add some charts to the frontend to show temperature over time
- Add bunch more APIs to get historical data and list of available weather stations
- May be throw in some tests

# Where's code
github.com/dreamiurg/weather-station

