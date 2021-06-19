# facebookTemplate


## Create a Facebook App and Page
The next step is to create an app and a page on Facebook. There is good [documentation](https://developers.facebook.com/docs/messenger-platform) available from Facebook but you'll walk through the main steps here.

### To create the app go [here](https://developers.facebook.com/) and
- click on My Apps -> Add a New App and enter a name 
- you will be redirected to the dashboard for the app
- under Products, find Add a Product and click on Messenger -> Set Up

### To create the page, you have to:
- go the settings for Messenger, scroll down to Token Generation and click on the link to create a new page for your app

Once you have created a page, go back to the Token Generation settings and select this page from the drop-down menu. Copy the Page - Access Token into the placeholder for `PAGE_ACCESS_TOKEN` in config.json. Set the `VERIFY_TOKEN` in the config.json to any random string.


## Set up the webhook
Finally, you need to register your webhook on the Facebook developers page.

- Go to the Messenger tab in Products again and scroll down to Webhooks, click on Setup Webhooks
- Under the Callback URL enter the url were your are running you app. in local host you can use [ngrok](https://ngrok.com/docs) to generate a public url for example, `https://51b6b3fa.ngrok.io/webhook`. It is important that your flask app is running at this point, because the `verify_token()` will be called on the next step.
- In the Verify Token field, you put the value you specified in your `config.json` file.
- In Subscription Fields make sure `messages` and `messaging_postbacks` are ticked Click Verify and Save to perform the authentication.


## Connect to your deployed bot
You can configure `BotID`, `LanguageCode`, `MessageType`, `ResponseType`, `refreshToken` in `config.json`. 

```json
{
    "BotID": "<BotId>",
    "IdToken": "<IdToken>",
    "LanguageCode": "English",
    "MessageType": "text",
    "PAGE_ACCESS_TOKEN": "<PAGE_ACCESS_TOKEN>",
    "ResponseType": "text",
    "VERIFY_TOKEN": "random string",
    "refreshToken": "<refresh_token>"
}
```

`BotID` and the `refreshToken` are provided to you in the Botlhale NLP Toolkit.