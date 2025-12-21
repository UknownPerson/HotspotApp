import ui

from winsdk.windows.networking.connectivity import NetworkInformation
from winsdk.windows.networking.networkoperators import NetworkOperatorTetheringManager, TetheringOperationalState

hotspot_ssid = "test"
hotspot_passphrase = "12345678"


async def enable(tethering_manager, ssid, passphrase):
    print("enabling...")

    config = tethering_manager.get_current_access_point_configuration()
    config.ssid = ssid
    config.passphrase = passphrase

    await tethering_manager.configure_access_point_async(config)
    return await tethering_manager.start_tethering_async()


async def disable(tethering_manager):
    print("disabling...")
    return await tethering_manager.stop_tethering_async()


# noinspection PyTypeChecker
async def main():
    internet_connection_profile = NetworkInformation.get_internet_connection_profile()

    if internet_connection_profile is None:
        print("No internet connection profile found.")
        return

    tethering_manager = NetworkOperatorTetheringManager.create_from_connection_profile(internet_connection_profile)

    if tethering_manager.tethering_operational_state == TetheringOperationalState.ON:
        await on_disabled(tethering_manager)
    else:
        await on_enabled(tethering_manager, hotspot_ssid, hotspot_passphrase)


async def getStates():
    internet_connection_profile = NetworkInformation.get_internet_connection_profile()
    if internet_connection_profile is None:
        print("No internet connection profile found.")
        return False

    tethering_manager = NetworkOperatorTetheringManager.create_from_connection_profile(internet_connection_profile)

    if tethering_manager.tethering_operational_state == TetheringOperationalState.ON:
        return True
    else:
        return False


if __name__ == "__main__":
    ui.run()
