import os
from pathlib import Path
from typing import Dict, List

class FileSystemManager:
    """
    Handles the discovery and movement of unstructured financial files.
    Acts as the foundational filesystem tool for our MCP/Agent setup.
    """
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.inbox_dir = self.base_dir / "data" / "inbox"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.reports_dir = self.base_dir / "data" / "reports"
        
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates required directories if they don't exist."""
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def scan_inbox(self) -> Dict[str, List[Path]]:
        """
        Scans the inbox directory and categorizes files by type.
        Returns a dictionary of categorized file paths.
        """
        files = {
            "csv": [],
            "pdf": [],
            "images": [],
            "unknown": []
        }
        
        if not self.inbox_dir.exists():
            return files

        image_exts = {'.png', '.jpg', '.jpeg'}

        for filepath in self.inbox_dir.iterdir():
            if not filepath.is_file():
                continue
                
            ext = filepath.suffix.lower()
            
            if ext == '.csv':
                files["csv"].append(filepath)
            elif ext == '.pdf':
                files["pdf"].append(filepath)
            elif ext in image_exts:
                files["images"].append(filepath)
            else:
                files["unknown"].append(filepath)
                
        return files