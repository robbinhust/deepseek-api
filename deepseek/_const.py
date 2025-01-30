DEVICE_INFO = {
    "protocol": 149,
    "xu": "mPmMidBWvfQ=",
    "version": "3.0.0",
    "hz": "c077wP0W8Yw=",
}

RSA_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDetfEgYD4aE1ZjmWJ6/jnPurhzI+yeRoJHWrnNtQMte3stQ4VjG3yu21FuN75E6cDpA9KtDXwcB2M/FiGUAe3G0rNotbWI8+SjZfUbW/OILFTzY0uaeEkmVGW5WyJ6weQbbr1xTCPa2OO3YIMeZljWUYHG5h21WAm/PATg8im8cQIDAQAB
-----END PUBLIC KEY-----'''

API_REG_DEVICE      = "https://fp-it-acc.portal101.cn/deviceprofile/v4"

BASE_API            = "https://chat.deepseek.com"

LOGIN_EP            = "/api/v0/users/login"                 # Login endpoint
COMPLETE_EP         = "/api/v0/chat/completion"             # Complete endpoint
USER_INFO_EP        = "/api/v0/users/current"               # User info endpoint
FETCH_FILE_EP       = "/api/v0/file/fetch_files"            # Fetch file status endpoint
UPLOAD_FILE_EP      = "/api/v0/file/upload_file"            # Upload file endpoint
FETCH_CHAT_SS_EP    = "/api/v0/chat_session/fetch_page"     # Get old conversation endpoint
DELETE_CHAT_SS_EP   = "/api/v0/chat_session/delete"         # Delete chat session endpoint
CREATE_SESSION_EP   = "/api/v0/chat_session/create"         # Create chat session (new conversation) endpoint
FETCH_CHAT_HIS_EP   = "/api/v0/chat/history_messages"       # Get chat history endpoint
CREATE_CHALLENGE_EP = "/api/v0/chat/create_pow_challenge"   # Create challenge endpoint


class FileStatus:
    SUCCESS       = "SUCCESS"
    PENDING       = "PENDING"
    CONTENT_EMPTY = "CONTENT_EMPTY"
