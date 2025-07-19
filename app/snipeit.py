# snipeit.py

import requests
import logging
from typing import Dict, Optional
from .logger import setup_logger

class SnipeITClient:
    def __init__(self, url: str, api_key: str, logger: logging.Logger):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.logger = logger

    def get_model_id(self, model_name: str, manufacturer: Optional[str]) -> Optional[int]:
        """Fetch model_id from Snipe-IT API based on model name and manufacturer."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            self.logger.debug(f"🔍 Fetching models from {self.url}/api/v1/models")
            response = requests.get(f"{self.url}/api/v1/models", headers=headers, timeout=10)
            response.raise_for_status()
            models = response.json().get("rows", [])
            
            for model in models:
                # Match model name (case-insensitive) and optionally manufacturer
                if model.get("name", "").lower() == model_name.lower():
                    if manufacturer and model.get("manufacturer"):
                        if model["manufacturer"].get("name", "").lower() == manufacturer.lower():
                            self.logger.debug(f"✅ Found model_id {model['id']} for model '{model_name}' and manufacturer '{manufacturer}'")
                            return model["id"]
                    elif not manufacturer:
                        self.logger.debug(f"✅ Found model_id {model['id']} for model '{model_name}' (no manufacturer check)")
                        return model["id"]
            
            self.logger.warning(f"⚠️ No matching model found for model '{model_name}' and manufacturer '{manufacturer}'")
            return None
        except requests.RequestException as e:
            self.logger.exception(f"❌ Exception fetching models from Snipe-IT: {e}")
            return None

    def sync_device(self, device: Dict[str, str]) -> None:
        asset_tag = device.get("name")
        serial = device.get("serial_no")
        model_name = device.get("model")
        manufacturer = device.get("make")

        if not asset_tag or not serial:
            self.logger.warning(f"⚠️ Missing asset tag or serial number for device: {device}")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Step 1: Check if asset exists
        try:
            check_url = f"{self.url}/api/v1/hardware/bytag/{asset_tag}"
            self.logger.debug(f"🔍 Checking asset with tag '{asset_tag}' at {check_url}")
            check_resp = requests.get(check_url, headers=headers, timeout=10)

            if check_resp.status_code == 200:
                try:
                    resp_json = check_resp.json()
                    self.logger.debug(f"📋 Asset check response: {resp_json}")
                    if resp_json.get("id") or (resp_json.get("rows") and len(resp_json.get("rows")) > 0):
                        self.logger.info(f"🟡 Asset with tag '{asset_tag}' already exists in Snipe-IT.")
                        return
                    else:
                        self.logger.debug(f"🟢 No asset found for tag '{asset_tag}', proceeding to create.")
                except ValueError:
                    self.logger.error(f"❌ Invalid JSON response from asset check: {check_resp.text}")
                    return
            elif check_resp.status_code == 404:
                self.logger.debug(f"🟢 No asset found for tag '{asset_tag}' (404), proceeding to create.")
            else:
                self.logger.error(f"❌ Error checking asset: {check_resp.status_code} - {check_resp.text}")
                return
        except requests.RequestException as e:
            self.logger.exception(f"❌ Exception checking existing asset in Snipe-IT: {e}")
            return

        # Step 2: Get model_id dynamically
        model_id = self.get_model_id(model_name, manufacturer)
        if not model_id:
            self.logger.error(f"❌ Could not determine model_id for model '{model_name}' and manufacturer '{manufacturer}'")
            return

        # Step 3: Proceed to create if asset not found
        asset_payload = {
            "asset_tag": asset_tag,
            "serial": serial,
            "model_id": model_id,
            "status_id": 2,
            "name": asset_tag
        }

        try:
            self.logger.debug(f"📡 Sending asset to Snipe-IT: {asset_payload}")
            response = requests.post(
                f"{self.url}/api/v1/hardware",
                json=asset_payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            resp_json = response.json()
            if resp_json.get("status") == "success":
                self.logger.info(f"✅ Asset '{asset_tag}' created in Snipe-IT: {resp_json.get('messages')}")
            else:
                self.logger.error(f"❌ Asset creation failed: {resp_json}")
        except requests.RequestException as e:
            self.logger.exception(f"❌ Exception posting to Snipe-IT: {e}")