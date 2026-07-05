import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tracker.database import Database
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

console = Console()

def show_dashboard():
    db = Database()
    courses = db.get_all_courses()
    stats = db.get_stats()

    console.print()
    console.print(Panel.fit(
        "[bold green]CERT AGENT DASHBOARD[/bold green]",
        border_style="green"
    ))

    stats_table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Count", justify="right")

    stats_table.add_row("Total Courses", str(stats['total']))
    stats_table.add_row("[green]Completed[/green]", f"[green]{stats['completed']}[/green]")
    stats_table.add_row("[yellow]In Progress[/yellow]", f"[yellow]{stats['in_progress']}[/yellow]")
    stats_table.add_row("[blue]Enrolled[/blue]", f"[blue]{stats['enrolled']}[/blue]")
    stats_table.add_row("[white]Discovered[/white]", f"[white]{stats['discovered']}[/white]")

    if stats['total'] > 0:
        progress = (stats['completed'] / stats['total']) * 100
        bar_len = 30
        filled = int(bar_len * stats['completed'] / stats['total'])
        bar = "#" * filled + "-" * (bar_len - filled)
        stats_table.add_row("", "")
        stats_table.add_row("Progress", f"[cyan]{bar}[/cyan] {progress:.1f}%")

    console.print(stats_table)
    console.print()

    if courses:
        status_colors = {
            "completed": "green",
            "in_progress": "yellow",
            "enrolled": "blue",
            "discovered": "white"
        }
        status_icons = {
            "completed": "[OK]",
            "in_progress": "[>>]",
            "enrolled": "[EN]",
            "discovered": "[??]"
        }

        courses_table = Table(title="Courses", box=box.ROUNDED, border_style="magenta")
        courses_table.add_column("#", justify="right", style="dim")
        courses_table.add_column("Status", justify="center")
        courses_table.add_column("Name", style="bold")
        courses_table.add_column("Platform")
        courses_table.add_column("Progress", justify="right")

        for i, c in enumerate(courses[:15], 1):
            color = status_colors.get(c['status'], 'white')
            icon = status_icons.get(c['status'], ' ')
            progress_bar = f"{c['progress']:.0f}%" if c['progress'] > 0 else "-"

            courses_table.add_row(
                str(i),
                f"[{color}]{icon}[/{color}]",
                c['name'][:45],
                c['platform'],
                progress_bar
            )

        if len(courses) > 15:
            courses_table.add_row("...", "", f"and {len(courses) - 15} more", "", "")

        console.print(courses_table)

    console.print()
    console.print("[dim]Run 'python main.py --learn' to start learning[/dim]")
    console.print("[dim]Run 'python main.py --schedule' for auto-pilot mode[/dim]")
    console.print()

if __name__ == "__main__":
    show_dashboard()
