"""Bridge between Tidal API and WiiM UPnP queue format.

The WiiM needs a SearchUrl pointing to a Tidal API playlist endpoint
to authenticate and fetch FLAC streams. For ad-hoc plays (songs, albums,
artists), we create a temporary Tidal playlist, push it to WiiM, then
delete it after playback starts.
"""

import html
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

import requests
import tidalapi
import urllib3

from wiim_device import api

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SESSION_FILE = Path.home() / ".tidal" / "session.json"
UPNP_PORT = 49152


def get_tidal_session() -> tidalapi.Session:
    """Load existing Tidal session from ~/.tidal/session.json."""
    session = tidalapi.Session()
    session.load_session_from_file(SESSION_FILE)
    if not session.check_login():
        raise RuntimeError("No valid Tidal session. Run `tidal login` first.")
    return session


def track_to_didl(track) -> str:
    """Convert a tidalapi Track to HTML-escaped DIDL-Lite XML for embedding in queue XML."""
    artist_id = track.artist.id if track.artist else ""
    album_id = track.album.id if track.album else ""
    album_art = ""
    if track.album and track.album.cover:
        album_art = f"https://resources.tidal.com/images/{track.album.cover.replace('-', '/')}/640x640.jpg"

    didl = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" '
        'xmlns:song="www.wiimu.com/song/" '
        'xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">'
        '<upnp:class>object.item.audioItem.musicTrack</upnp:class>'
        '<item id="">'
        f'<song:singerid>{artist_id}</song:singerid>'
        f'<song:albumid>{album_id}</song:albumid>'
        '<res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration=""></res>'
        f'<dc:title>{escape(track.name)}</dc:title>'
        f'<upnp:artist>{escape(track.artist.name)}</upnp:artist>'
        f'<upnp:album>{escape(track.album.name)}</upnp:album>'
        f'<upnp:albumArtURI>{escape(album_art)}</upnp:albumArtURI>'
        '</item>'
        '</DIDL-Lite>'
    )
    return html.escape(didl)


def build_queue_xml(name: str, tracks: list, playlist_id: str = "") -> str:
    """Build WiiM PlayList queue XML from Tidal tracks. Requires playlist_id for SearchUrl."""
    search_url = (
        f"https://api.tidal.com/v1/playlists/{playlist_id}/items"
        f"?countryCode=FR&amp;order=INDEX&amp;orderDirection=ASC&amp;offset=0&amp;limit=100"
    )

    track_xml = ""
    for i, track in enumerate(tracks, 1):
        track_xml += (
            f"<Track{i}>"
            f"<Id>{track.id}</Id>"
            f"<URL></URL>"
            f"<Metadata>{track_to_didl(track)}</Metadata>"
            f"<Source>Tidal</Source>"
            f"</Track{i}>\n"
        )

    pic_url = ""
    if tracks and tracks[0].album and tracks[0].album.cover:
        pic_url = f"https://resources.tidal.com/images/{tracks[0].album.cover.replace('-', '/')}/320x320.jpg"

    return (
        '<?xml version="1.0"?>\n'
        '<PlayList>\n'
        f'<ListName>{escape(name)}</ListName>\n'
        '<ListInfo>\n'
        '<QueueVersion>2.0</QueueVersion>\n'
        '<SourceName>Tidal</SourceName>\n'
        f'<PicUrl>{escape(pic_url)}</PicUrl>\n'
        '<ContentType>songlist</ContentType>\n'
        f'<SearchUrl>{search_url}</SearchUrl>\n'
        f'<TotalNumber>{len(tracks)}</TotalNumber>\n'
        f'<TrackNumber>{len(tracks)}</TrackNumber>\n'
        '<LastPlayIndex>0</LastPlayIndex>\n'
        '</ListInfo>\n'
        '<Tracks>\n'
        f'{track_xml}'
        '</Tracks>\n'
        '</PlayList>'
    )


def push_queue_and_play(host: str, queue_name: str, queue_xml: str, index: int = 0):
    """Send a queue to WiiM via UPnP SOAP and start playback.

    Uses curl with temp files to avoid shell escaping issues with complex XML.
    """
    import tempfile

    escaped = html.escape(queue_xml)
    url = f"http://{host}:{UPNP_PORT}/upnp/control/PlayQueue1"
    ns = "urn:schemas-wiimu-com:service:PlayQueue:1"

    import time
    api(host, "setPlayerCmd:stop")
    time.sleep(1)

    create_soap = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
        '<s:Body>'
        f'<u:CreateQueue xmlns:u="{ns}">'
        f'<QueueContext>{escaped}</QueueContext>'
        '</u:CreateQueue>'
        '</s:Body></s:Envelope>'
    )
    soap_file = Path("/tmp/wiim_queue.xml")
    soap_file.write_text(create_soap)

    subprocess.run([
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: text/xml; charset=utf-8",
        "-H", f'SOAPAction: "{ns}#CreateQueue"',
        "-d", f"@{soap_file}",
    ], capture_output=True, timeout=10)

    play_soap = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
        '<s:Body>'
        f'<u:PlayQueueWithIndex xmlns:u="{ns}">'
        f'<QueueName>{escape(queue_name)}</QueueName>'
        f'<Index>{index}</Index>'
        '</u:PlayQueueWithIndex>'
        '</s:Body></s:Envelope>'
    )
    subprocess.run([
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: text/xml; charset=utf-8",
        "-H", f'SOAPAction: "{ns}#PlayQueueWithIndex"',
        "-d", play_soap,
    ], capture_output=True, timeout=10)

    soap_file.unlink(missing_ok=True)


def create_temp_playlist_and_play(session: tidalapi.Session, host: str, name: str, tracks: list) -> str:
    """Create a Tidal playlist, push to WiiM, and start native playback.

    Returns the playlist ID. The playlist must stay alive while the WiiM is
    streaming (it uses the SearchUrl to re-authenticate with Tidal).
    """
    import time
    track_ids = [str(t.id) for t in tracks]
    playlist = session.user.create_playlist(f"[WiiM] {name}", "")
    playlist.add(track_ids)
    time.sleep(2)  # Wait for Tidal to propagate the playlist

    queue_xml = build_queue_xml(name, tracks, playlist_id=playlist.id)
    push_queue_and_play(host, name, queue_xml)
    return playlist.id
