# Transport for Wales automated announcements

Freedom of Information requests have allowed members of the public to request a copy of Transport for Wales Rail Limited's on-board train annoucement recordings for personal use.

This repository offers the results of this Freedom of Information request to the general public without the administrative burden of submitting a FOI request to TfWRL.

> 🚄🔊 [I just want to look at the full set of announcements!](downloads/)

## Automatic downloader

The repository has a Python script (`downloader.py`) at its root which can be used in conjunction with your own access to TfW's Objective Connect portal for accessing their announcement portfolio.

TfW require one-time access codes each time your access the workspace, which this script accounts for.

### Running the downloader

You'll need Python 3.10 or later to run this script.

1. Install the necessary requirements with `pip`:

```
pip install -r requirements.txt
```

2. Run the script

```
python downloader.py
```

3. When prompted, enter your Objective Connect login details.
4. Select the appropriate workspace from the list presented.
5. If needed, check your email for a one-time access code and enter it when prompted.
6. Watch as your internet bandwidth is used on train announcements!

### File naming scheme

When using the downloader, files are automatically saved to a `downloads` folder next to the script.

Files are named in this format: `<name>_<uuid>_v<file version>.<extension>`.

### Automating authentication

If you're using the script a lot and would like to save your login details, you can do so.

Create an `auth.json` file next to the script and fill it in as shown below:

```json
{
  "username": "example@tfw.wales",
  "password": "transportForWales1"
}
```
