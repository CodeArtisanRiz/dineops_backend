import random
import string
from datetime import timedelta
from django.utils import timezone

def generate_email_otp():
    """Generate OTP and token for email verification"""
    otp = ''.join(random.choices(string.digits, k=6))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # TODO: Send email with OTP
    return otp, token

def generate_phone_otp():
    """Generate OTP for phone verification"""
    otp = ''.join(random.choices(string.digits, k=6))
    
    # TODO: Send SMS with OTP
    return otp

def generate_verification_data(method='phone'):
    """Generate OTP and verification token"""
    if method == 'email':
        otp, token = generate_email_otp()
    else:
        otp = generate_phone_otp()
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # Print for testing purposes
    print(f"\n=== TEST OTP DATA ===")
    print(f"OTP: {otp}")
    print(f"Token: {token}")
    print("===================\n")
    
    return otp, token

def verify_otp(verification_record, submitted_otp):
    """Verify the OTP"""
    if verification_record.is_verified:
        return False, "Already verified"
        
    if verification_record.expires_at < timezone.now():
        return False, "OTP expired"
        
    if verification_record.attempts >= 3:
        return False, "Too many attempts"
    
    if submitted_otp == verification_record.verification_id[:6]:
        return True, "Verified successfully"
    
    return False, "Invalid OTP"