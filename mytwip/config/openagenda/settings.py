import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_FOLDER = Path(__file__).resolve().parent.parent.parent.parent

# Data directories
DATA_FOLDER = f"{BASE_FOLDER}/data/openagenda"
TMP_FOLDER = f"{BASE_FOLDER}/tmp/openagenda"
LOG_FOLDER = f"{BASE_FOLDER}/log/openagenda"
EVENTS_FOLDER = f"{DATA_FOLDER}/events"

# Data files
EVENTS_STORE_TPL = f"{EVENTS_FOLDER}/[[agenda_uid]].json"

# Ensure directories exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(EVENTS_FOLDER, exist_ok=True)

# Data files
AGENDAS_STORE = f"{DATA_FOLDER}/agendas.json"

# URL templates
OPENAGENDA_PUBLIC_KEY = os.getenv("OPENAGENDA_PUBLIC_KEY")
OPENAGENDA_QUERY_SIZE = 100  # Default size for queries
OPENAGENDA_MAX_PAGES = 10  # Maximum number of pages to fetch
URL_TPL_START = f"https://api.openagenda.com/v2/agendas"
URL_TPL_DEFAULT_PARAMS = f"?key={OPENAGENDA_PUBLIC_KEY}&size={OPENAGENDA_QUERY_SIZE}"
URL_TPL_AGENDAS_SEARCH = f"{URL_TPL_START}{URL_TPL_DEFAULT_PARAMS}&search=[[search_term]]"
URL_TPL_AGENDAS_BY_SLUG = f"{URL_TPL_START}{URL_TPL_DEFAULT_PARAMS}&slug[]=[[search_slug]]"
URL_TPL_AGENDAS_DETAILS = f"{URL_TPL_START}/[[agenda_uid]]{URL_TPL_DEFAULT_PARAMS}"
URL_TPL_EVENTS_BY_AGENDA_UID = f"{URL_TPL_START}/[[agenda_uid]]/events{URL_TPL_DEFAULT_PARAMS}&sort=updatedAt.desc"

# CACHING PARAMETERS
CACHING_DURATION = 86400
