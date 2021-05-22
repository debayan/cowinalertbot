# cowin Telegram alert bot

This sends vaccination slot alerts for folks in India who are using the cowin platform for booking them. This bot requires an auth token to operate. The public API is not accurate and hence using an authenticated bot is better.

## Installation

```sh
git clone https://github.com/debayan/cowinalertbot.git
cd cowinalertbot
virtualenv -p python3.8 .
source bin/activate
pip3 install notifiers requests

```

Now you need to fill up the sandboxconfig.ini file with the required data

```sh
telegramchatid=
district_ids=
telegramtoken=
cowinauth=
```

First, you need to create a Telegram channel using the app, then you need to create a Telegram bot. Add the bot to this channel and make it admin. When you create the bot you will be given the bot token. Paste that for the field 'telegramtoken'.  To get the 'telegramchat' ID follow https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35.

For 'district_ids' find the IDs for the district to track using Chrome developer tools. Open https://www.cowin.gov.in/home and select the district you want and click Search. Now right click on search button and click Inspect button. Click network tab on top. Click Search again and see the URl which is being hit. The URL contains the district ID. You may give comma separated district IDs in the config file.

For 'cowinauth' field, do the same as above, but login first using your Indian mobile number. When you check the Network tab in developr tools, note the 'auth' token in Requests field, it will look like  "Bearer " and then a long string. Copy this whole thing along with 'Bearer' and paste in config file.
