# PayMob Environment Configuration Guide

## Required Environment Variables

Add these keys to your `.env` file for proper PayMob integration:

```env
# PayMob Configuration (Test Environment)
PAYMOB_API_KEY=your_api_key_here
PAYMOB_INTEGRATION_ID=your_integration_id_here
PAYMOB_IFRAME_ID=your_iframe_id_here
PAYMOB_BASE_URL=https://accept.paymob.com/api
PAYMOB_HMAC_SECRET=your_hmac_secret_here

# PayMob Test Cards
# Success Card: 4987654321098769
# Failure Card: Any other card number (e.g., 4000000000000002)
```

## How to Get PayMob Credentials

### 1. API Key
- Login to your PayMob dashboard
- Go to **Settings** → **API Keys**
- Copy your **API Key**

### 2. Integration ID
- Go to **Payment Integrations**
- Select your integration method (Card, Wallet, etc.)
- Copy the **Integration ID**

### 3. iFrame ID
- Go to **Payment Integrations** → **iFrames**
- Copy your **iFrame ID**

### 4. HMAC Secret ⚠️ **CRITICAL**
- Contact PayMob support to get your HMAC secret
- Email: support@paymob.com
- This is required for webhook security verification
- **Without this, your webhooks are vulnerable to attacks**

## Current Configuration Status

✅ **PAYMOB_API_KEY**: Configured
✅ **PAYMOB_INTEGRATION_ID**: Configured (5242071)
✅ **PAYMOB_IFRAME_ID**: Configured (951380)
✅ **PAYMOB_BASE_URL**: Configured
❌ **PAYMOB_HMAC_SECRET**: **MISSING - CRITICAL**

## Test Environment vs Production

### Test Environment (Current)
```env
PAYMOB_BASE_URL=https://accept.paymob.com/api
```

### Production Environment
```env
PAYMOB_BASE_URL=https://accept.paymob.com/api
```
*Note: PayMob uses the same base URL for both test and production*

## Test Cards for PayMob

### Success Scenarios
- **4987654321098769** - Always successful
- **4111111111111111** - Visa test card
- **5123456789012346** - Mastercard test card

### Failure Scenarios
- **4000000000000002** - Card declined
- **4000000000000069** - Expired card
- **4000000000000119** - Processing error
- Any other card number will typically fail

## Security Notes

1. **HMAC Secret**: This is the most critical security component
   - Used to verify webhook authenticity
   - Prevents fake payment notifications
   - Must be kept secret and secure

2. **API Key**: Keep this secure
   - Used for API authentication
   - Should not be exposed in client-side code

3. **Integration ID**: Less sensitive but still important
   - Identifies your payment integration
   - Can be exposed in client-side code

## Webhook Configuration

In your PayMob dashboard, set your webhook URL to:
```
https://yourdomain.com/api/accounts/paymob-webhook/
```

Make sure to:
1. Enable webhook notifications
2. Select the events you want to receive
3. Test the webhook endpoint

## Testing Your Configuration

Run the test script to verify your configuration:

```bash
# Python test script
python test_paymob_integration.py

# Or bash script
chmod +x quick_test_paymob.sh
./quick_test_paymob.sh
```

## Troubleshooting

### Common Issues

1. **"PAYMOB_HMAC_SECRET not configured"**
   - Add the HMAC secret to your .env file
   - Contact PayMob support if you don't have it

2. **"PayMob authentication failed"**
   - Check your API key
   - Ensure it's not expired
   - Verify you're using the correct environment

3. **"Webhook signature verification failed"**
   - Verify HMAC secret is correct
   - Check webhook data format
   - Ensure proper header names

4. **"Payment not found for order ID"**
   - Check database for payment records
   - Verify order ID mapping
   - Check for timing issues

### Debug Mode

Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'paymob_debug.log',
        },
    },
    'loggers': {
        'accounts.services': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Next Steps

1. **Get HMAC Secret**: Contact PayMob support immediately
2. **Update .env file**: Add the HMAC secret when you receive it
3. **Test Integration**: Run the test scripts
4. **Configure Webhooks**: Set up webhook URL in PayMob dashboard
5. **Go Live**: Switch to production credentials when ready

## Support

- **PayMob Support**: support@paymob.com
- **PayMob Documentation**: https://developers.paymob.com/
- **PayMob Dashboard**: https://accept.paymob.com/

---

**⚠️ IMPORTANT**: Your integration is currently **NOT SECURE** without the HMAC secret. Please get this from PayMob support as soon as possible.
