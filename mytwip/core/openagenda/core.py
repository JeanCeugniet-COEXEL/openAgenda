"""
For utils
"""
from mytwip.config.openagenda.settings import *
from mytwip.core.openagenda.core import *
from mytwip.utils.common import *
import logging
import urllib.parse
import requests
import time
import copy

openagenda_last_access = None
"""
Core utilities for OpenAgenda API
"""
# Query to openAgenda API
def openagenda_query(query_url: str, data_type="items", headers: dict = {"Accept": "application/json"}) -> dict:
    global openagenda_last_access
    if openagenda_last_access is not None:
        if (timestamp() - openagenda_last_access) < 1:
            logger.warning("OpenAgenda API rate limit reached, waiting for 1 second")
            time.sleep(1)

    result = {"status": "unknown", "msg": "Unkown status"}
    logger.info(f"Executing OpenAgenda query: {query_url}")
    try:
        response = requests.get(query_url, headers=headers)
        logger.info("response : %s", response.json())
        if response.status_code == 404:
            logger.warning("Query %s returned empty set %s : %s", query_url, response.status_code, response.text)
            result = {"status": "success", "msg": "OpenAgenda query successful", "data": {data_type: [], "total":0}}
        elif response.status_code != 200:
            logger.warning("Query %s returned error %s : %s", query_url, response.status_code, response.text)
            result = {"status": "error", "msg": "Error during OpenAgenda query", "data": response.json()}
        else:
            logger.info("response 200")
            result = {"status": "success", "msg": f"OpenAgenda query successful", "data": response.json()}
    except Exception as e:
        logger.error("Error during OpenAgenda query %s : %s", query_url, e)
        result = {"status": "error", "msg": f"Error during OpenAgenda query: {str(e)}"}

    if data_type not in result["data"] and "uid" in result["data"]:
        result["data"] = {data_type: [result["data"]], "total": 1}
    logger.info("result : %s", result)

    result_to_log = copy.deepcopy(result)
    if result_to_log["data"].get("agendas"):
        result_to_log["data"]["agendas"] = f"{len(result_to_log["data"]["agendas"])} items"
    if result_to_log["data"].get("events"):
        result_to_log["data"]["events"] = f"{len(result_to_log["data"]["events"])} items"
    logger.info("query result data : %s", result_to_log["data"])

    openagenda_last_access = timestamp()
    return result

# Handle pagination for large result sets
def openagenda_paginate(data: dict, query_url: str, data_type: str = "items")->dict:
    logger.info(f"openagenda_paginate(agendas : {len(data.get("agendas", []))} / events : {len(data.get("events", []))}")
    logger.info("after : %s", data.get("after", None))
    items_type = "agendas" if "agendas" in data else "events" if "events" in data else None
    page_result = None
    if (items_type is None) or ("after" not in data):
        result = data
    else:
        items = data.get(items_type)
        nb_items = data.get("total", 0)
        logger.info("nb_items : %s", nb_items)
        nb_pages_to_query = min(nb_items // OPENAGENDA_QUERY_SIZE, OPENAGENDA_MAX_PAGES)
        if nb_items % OPENAGENDA_QUERY_SIZE > 0:
            nb_pages_to_query += 1
        logger.info("nb_pages_to_query : %s", nb_pages_to_query)
        for page in range(2, nb_pages_to_query + 1):
            if True:
                """
            if items_type == "agendas":
                page_query_url = f"{query_url}&page={page}"
            elif items_type== "events":
            """
                after = data.get("after", []) if page_result is None else page_result["data"].get("after", [])
                if len(after) != 2:
                    break
                page_query_url = f"{query_url}&after[]={after[0]}&after[]={after[1]}"
            logger.info("page_query_url : %s", page_query_url)
            page_result = openagenda_query(page_query_url, data_type)
            if page_result["status"] == "success":
                items+= page_result["data"].get(items_type, [])

        result = {
            items_type: items,
            "total": nb_items,
            "pages": nb_pages_to_query
        }

    return result

# AGENDAS >>
# Search agendas by search term
def agendas_search(search_term: str) -> dict:
    """
    Search for OpenAgenda agendas by search term
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    agendas = []
    # Placeholder for actual search logic
    logger.info(f"Searching for agendas with term: {search_term}")
    query_url = URL_TPL_AGENDAS_SEARCH.replace("[[search_term]]", urllib.parse.quote(search_term))
    query_result = openagenda_query(query_url, "agendas")
    if query_result["status"] == "success":
        query_result["data"] = openagenda_paginate(query_result["data"], query_url, "agendas")
        agendas = query_result["data"].get("agendas", [])
        result = {
            "status": "success",
            "msg": f"Found {query_result["data"].get("total", 0)} agendas for search term '{search_term}'",
            "data": query_result["data"]
        }
    else:
        result = query_result

    agendas_update(agendas)

    return result

# Search agendas by slug
def agendas_by_slug(search_slug: str) -> dict:
    """
    Search for OpenAgenda agendas by slug
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    agendas = []
    agenda = None
    # Placeholder for actual search logic
    logger.info(f"Searching for agendas with slug: {search_slug}")
    query_url = URL_TPL_AGENDAS_BY_SLUG.replace("[[search_slug]]", urllib.parse.quote(str(search_slug)))
    query_result = openagenda_query(query_url, "agendas")
    logger.info("query_result", query_result)
    if query_result["status"] == "success":
        query_result["data"] = openagenda_paginate(query_result["data"], query_url, "agendas")
        agendas = query_result["data"].get("agendas", [])
        result = {
            "status": "success",
            "msg": f"Found {len(agendas)} agendas for search slug '{search_slug}'",
            "data": query_result["data"]
        }
    else:
        result = query_result

    agendas_update(agendas)

    return result

# Search agendas details by uid
def agendas_details(agenda_uid: int) -> dict:
    """
    Search for OpenAgenda agendas by uid
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    agendas = []
    agenda = None
    # Placeholder for actual search logic
    logger.info(f"Searching for agendas with uid: {agenda_uid}")
    query_url = URL_TPL_AGENDAS_DETAILS.replace("[[agenda_uid]]", urllib.parse.quote(str(agenda_uid)))
    query_result = openagenda_query(query_url, "agendas")
    logger.info("query_result : %s", query_result)
    if query_result["status"] == "success":
        agendas = query_result.get("data", {}).get("agendas", [])
        agenda = agendas[0] if len(agendas) else None
        msg = f"Found agenda for uid '{agenda_uid}'" if agenda is not None else f"Found no agenda for uid '{agenda_uid}'"
        result = {
            "status": "success",
            "msg": msg,
            "data": {
                "agenda": agenda,
            }
        }
    else:
        result = query_result

    agendas_update(agendas)

    return result

# Load agendas data
def agendas_load()-> list[dict]:
    result = []

    if os.path.exists(AGENDAS_STORE):
        with open(AGENDAS_STORE, "r") as file_in:
            result = json.load(file_in)

    return result

# Store agendas data
def agendas_store(agendas: list[dict]) -> bool:
    result = False
    try:
        with open(AGENDAS_STORE, "w") as file_out:
            file_out.write(json.dumps(agendas))
        result = True
    except IOError as e:
        logger.error("Error during agendas store : %s", str(e))

    return result

# Update agendas data
def agendas_update(new_agendas: list[dict]) -> bool:
    known_agendas = agendas_load()
    known_agendas_uids = [agenda.get("uid") for agenda in known_agendas]
    known_uids_to_indexes = {agenda.get("uid"): index for index, agenda in enumerate(known_agendas)}
    new_uids_to_indexes = {agenda.get("uid"): index for index, agenda in enumerate(new_agendas)}
    agendas_to_update = [agenda for agenda in new_agendas if agenda.get("uid") in known_agendas_uids]
    nb_updates = 0
    for agenda in agendas_to_update:
        nb_updates+= 1
        uid = agenda.get("uid")
        known_index = known_uids_to_indexes[uid]
        new_index = new_uids_to_indexes[uid]
        known_agendas[known_index].update(new_agendas[new_index])
    agendas_to_add = [agenda for agenda in new_agendas if agenda.get("uid") not in known_agendas_uids]
    nb_adds = len(agendas_to_add)
    logger.info("agendas update : nb updates : %s / nb add : %s", nb_updates, nb_adds)
    known_agendas+= agendas_to_add
    agendas_store(known_agendas)

# AGENDAS >>
# EVENTS >>
def events_by_agenda_uid(agenda_uid: int) -> dict:
    """
    Search for OpenAgenda events by agenda uid
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    events = []
    # Placeholder for actual search logic
    logger.info(f"Searching for events by agenda uid : {agenda_uid}")
    query_url = URL_TPL_EVENTS_BY_AGENDA_UID.replace("[[agenda_uid]]", urllib.parse.quote(str(agenda_uid)))
    query_result = openagenda_query(query_url, "events")
    if query_result["status"] == "success":
        query_result["data"] = openagenda_paginate(query_result["data"], query_url, "events")
        events = query_result["data"].get("events", [])
        result = {
            "status": "success",
            "msg": f"Found {query_result["data"].get("total", 0)} events for agenda uid '{agenda_uid}'",
            "data": query_result["data"]
        }
    else:
        result = query_result

    events_update(agenda_uid, events)

    return result

# Load events data
def events_load(agenda_uid)-> list[dict]:
    result = []

    events_store_path = EVENTS_STORE_TPL.replace("[[agenda_uid]]", urllib.parse.quote(str(agenda_uid)))
    if os.path.exists(events_store_path):
        with open(events_store_path, "r") as file_in:
            result = json.load(file_in)

    return result

# Store events data
def events_store(agenda_uid: int, events: list[dict]) -> bool:
    result = False

    events_store_path = EVENTS_STORE_TPL.replace("[[agenda_uid]]", urllib.parse.quote(str(agenda_uid)))
    try:
        with open(events_store_path, "w") as file_out:
            file_out.write(json.dumps(events))
        result = True
    except IOError as e:
        logger.error("Error during agendas store : %s", str(e))

    return result

# Update events data
def events_update(agenda_uid: int, new_events: list[dict]) -> bool:
    known_events = events_load(agenda_uid)
    known_events_uids = [event.get("uid") for event in known_events]
    known_uids_to_indexes = {event.get("uid"): index for index, event in enumerate(known_events)}
    new_uids_to_indexes = {event.get("uid"): index for index, event in enumerate(new_events)}
    events_to_update = [event for event in new_events if event.get("uid") in known_events_uids]
    nb_updates = 0
    for event in events_to_update:
        nb_updates+= 1
        uid = event.get("uid")
        known_index = known_uids_to_indexes[uid]
        new_index = new_uids_to_indexes[uid]
        known_events[known_index].update(new_events[new_index])
    events_to_add = [event for event in new_events if event.get("uid") not in known_events_uids]
    nb_adds = len(events_to_add)
    logger.info("events update : nb updates : %s / nb add : %s", nb_updates, nb_adds)
    known_events+= events_to_add
    events_store(agenda_uid, known_events)

# << EVENTS

"""
UTILS >>
"""
logger = None

"""
Logging
"""
def logger_init():
    global logger
    logger = logging.getLogger(__name__)
    current_date = datetime.now().strftime('%Y%m%d')
    logging.basicConfig(filename=f'{LOG_FOLDER}/{current_date}.log', format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d]\n%(message)s', datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

    return logger

"""
Récupération dossier temporaire du jour
"""
def get_tmp_folder() -> str|bool:
    result = f"{TMP_FOLDER}/{datetime.now().strftime("%Y-%m-%d")}"
    try:
        os.makedirs(result, exist_ok=True)
    except:
        result = None
        logger.error("Could not create tmp folder %s", result)
        raise Exception(f"Could not create tmp folder {result}")
    
    return result

"""
Nettoyage des dossiers temporaires, à l'exception du jour courant
"""
def cleanup_tmp_folders() -> bool:
    result = False
    current_tmp_folder = get_tmp_folder()
    try:
        for entry in os.listdir(TMP_FOLDER):
            fullpath = f"{TMP_FOLDER}/{entry}"
            if (os.path.isdir(fullpath)) and (fullpath != current_tmp_folder):
                os.rmdir(fullpath)
    except:
        pass
    else:
        result = True

    return result


"""
<< UTILS
"""

if __name__ == "__main__":
    raise Exception("Should be used only as import")