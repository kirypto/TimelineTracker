# Application Setup

- Locate and download the `Deployable` zip from [the releases page][projectReleases].

## Requirements

- Install Python _(version >= 3.9)_ and pip.
- Install the required packages _(`pip install -r requirements.txt`)_.

## App Configuration

- Create a configuration file in the root TTAPI directory for project configuration. _(Recommended name is `config.yaml`, as that is the
  expected name by the script below)_
- If intending to run the API on anything other than `http://localhost:5000`, it is recommended to change the `servers` list in the
  `apiSpecification.json` file. This will allow the Swagger docs page to interact with your API.
- See the [Sample Config](sampleConfig.md) for an example.
    - Note: if going with Auth0.com _(recommended)_, see below for instructions.

### Auth0.com Configuration
- To securely manage authentication, Auth0.com can be used. It provides a free *(up to an extent, such as limited user count)* service for
  managing users, authentication, access, etc. This is the recommended approach for deploying TTAPI.
- Auth0.com provides a [Getting Started](https://auth0.com/docs/quickstart/webapp/python) document that covers integration into a python
  app.
    - **Note:** This guide targets users creating an app and includes the python code which **will not be needed** for setting up TTAPI.
      Only the steps for setting up the application are necessary.
    - The [Get Your Application Keys](https://auth0.com/docs/quickstart/webapp/python#get-your-application-keys) section describes how to
      create the application for TTAPI. You can use the default application _(created when you create your Auth0.com account)_ or create one
      specifically for TTAPI. If you do create one, ensure you create a Regular Web Application type.
    - The [Configure Callback Urls](https://auth0.com/docs/quickstart/webapp/python#configure-callback-urls) section describes how to add
      your callback url to return to when auth is successful. If you are just running TTAPI locally, then this will be
      `http://localhost:<port>/auth-callback`. If you are running it elsewhere, substitute your IP or hostname accordingly.
    - The [Configure Logout Urls](https://auth0.com/docs/quickstart/webapp/python#configure-logout-urls) section describes how to set
      allowed return routes for after a client logs out.
- Ensure you have configured the following. Note that these examples are for an application running on `localhost` and should be adjusted
  accordingly if otherwise.
    - Basic Information:
        - Copy the Domain, Client ID, and Client Secret values into the `config.yaml` file.
    - Application URIs:
        - Add `http://localhost:5000/auth-callback` to the Allowed Callback URLs.
        - Add`http://localhost:5000/home` to the Allowed Logout URLs.


## Running the API

- From PowerShell _(windows)_:
    - Read and confirm the settings of the `runWithFlask.ps1`
    - Run it from the root TTAPI directory: `./Script/runWithflask.ps1`
- From bash _(linux/mac)_:
    - Read and confirm the settings of the `runWithFlask.ps1`
    - Run it from the root TTAPI directory: `./Script/runWithflask.ps1`

[projectReleases]: https://github.com/kirypto/TimelineTracker/releases/latest