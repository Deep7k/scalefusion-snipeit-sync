import requests
import logging
from typing import Dict, Optional
from .logger import setup_logger

class SnipeITClient:
    def __init__(self, url: str, api_key: str, logger: logging.Logger):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.logger = logger

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
            check_resp = requests.get(check_url, headers=headers, timeout=10)

            if check_resp.status_code == 200:
                self.logger.info(f"🟡 Asset with tag '{asset_tag}' already exists in Snipe-IT.")
                return  # Exit early — asset already exists

            elif check_resp.status_code != 404:
                # 404 is okay (not found), but anything else is an issue
                self.logger.error(f"❌ Error checking asset: {check_resp.status_code} - {check_resp.text}")
                return
        except requests.RequestException as e:
            self.logger.exception(f"❌ Exception checking existing asset in Snipe-IT: {e}")
            return

        # Step 2: Proceed to create if asset not found
        asset_payload = {
            "asset_tag": asset_tag,
            "serial": serial,
            "model_id": 2,  # TODO: Dynamically resolve
            "status_id": 2,  # TODO: Dynamically resolve
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
