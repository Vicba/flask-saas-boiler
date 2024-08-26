# Flask Saas backend starter

TODO
- [] NEEDS CLEANUP in auth

make sure stripe cli is listening to /api/payment/webhook

# Tech Stack
- Flask
- MongoDB
- Stripe
- Google OAuth

### Google Auth
1. Set up a Google OAuth 2.0 client ID and secret in the Google Developers Console.
2. Set the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables to the values from the Google Developers Console.

# Scripts

 A common recommendation is to start with (2 x $server_num_cpu_cores) + 1 t

```bash
gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:5000 app:app
```
