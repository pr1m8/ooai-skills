from __future__ import annotations
from rich.console import Console
from .models import SkillIndex
from .s3 import S3Client
from .settings import OoaiSkillsSettings

def remote_stats(settings: OoaiSkillsSettings, *, console: Console | None=None) -> None:
    con = console or Console()
    s3 = S3Client.from_settings(settings)
    idx = SkillIndex.model_validate(s3.get_json('index/skills.json') or {'skills': []})
    con.print(f'Bucket: [bold]{settings.bucket}[/bold]')
    con.print(f'Skills indexed: [bold]{len(idx.skills)}[/bold]')
