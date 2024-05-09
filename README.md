Basic MicroMDM
==============

This is a basic/simplistic [MicroMDM](https://micromdm.io/) setup to keep configuration profiles up-to-date. The approach is to regularly fetch a profile list from all managed devices and check whether the correct version of the required profile(s) is/are installed.

The configuration profile(s) should be uploaded to the MicroMDM server and be referenced in a blueprint. This will make MicroMDM install them upon device enrolment. To deploy a new version, upload a profile with the same ID but a different/new UUID.

Components/services are:

- `micromdm`: the MicroMDM server itself

- `webhook`: a simple webhook service that receives ProfileLists sent back by devices, checks whether required profiles are present and triggers install/update as needed

- `checker`: (not implemented yet) a service that regularly issues an MDM command to all managed devices to get a profile list

Configuration in `.env` file:

- `MICROMDM_API_KEY`: secret API key to run commands on MicroMDM server
- `MICROMDM_SERVER_URL`: public URL under which clients reach the MicroMDM server (the assumption is that this service sits behind a reverse proxy taking care of TLS termination)
- `MICROMDM_PORT`: local port for the MicroMDM server (optional, default: `8080`)

