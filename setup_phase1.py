#!/usr/bin/env python3
"""
Autohire V2.0 - Phase 1 Automated Setup Script

Installs and validates all Phase 1 dependencies:
- Camoufox browser with Melbourne configuration
- Nesta Skills Extractor with language models
- Enhanced anti-detection components

Usage:
    python setup_phase1.py [--check-only] [--verbose]
"""
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase1Installer:
    """Automated installer for Autohire V2.0 Phase 1 components"""

    def __init__(self, check_only: bool = False, verbose: bool = False):
        self.check_only = check_only
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.backend_root = self.project_root / "backend"
        self.requirements_file = self.backend_root / "requirements_operator_v2.txt"

        if verbose:
            logger.setLevel(logging.DEBUG)

        # Installation status
        self.results = {
            "python_version": False,
            "requirements": False,
            "camoufox_binary": False,
            "spacy_model": False,
            "tesseract_ocr": False,
        }

    def run(self) -> bool:
        """Execute complete setup process"""
        logger.info("=" * 60)
        logger.info("Autohire V2.0 - Phase 1 Installation")
        logger.info("=" * 60)

        if self.check_only:
            logger.info("Running in CHECK-ONLY mode (no installations)")

        # Step 1: Check Python version
        self.check_python_version()

        # Step 2: Install Python dependencies
        if not self.check_only:
            self.install_requirements()
        else:
            self.check_requirements()

        # Step 3: Download Camoufox browser binary
        if not self.check_only:
            self.install_camoufox_binary()
        else:
            self.check_camoufox_binary()

        # Step 4: Download Spacy language model
        if not self.check_only:
            self.install_spacy_model()
        else:
            self.check_spacy_model()

        # Step 5: Check Tesseract OCR (manual install)
        self.check_tesseract_ocr()

        # Step 6: Validate installations
        success = self.validate_installations()

        # Print summary
        self.print_summary()

        return success

    def check_python_version(self) -> bool:
        """Verify Python 3.11+ is installed"""
        logger.info("\n[1/5] Checking Python version...")

        version = sys.version_info
        required = (3, 11)

        if version >= required:
            logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
            self.results["python_version"] = True
            return True
        else:
            logger.error(
                f"❌ Python {required[0]}.{required[1]}+ required, "
                f"found {version.major}.{version.minor}"
            )
            self.results["python_version"] = False
            return False

    def install_requirements(self) -> bool:
        """Install Python dependencies from requirements_operator_v2.txt"""
        logger.info("\n[2/5] Installing Python dependencies...")

        if not self.requirements_file.exists():
            logger.error(f"❌ Requirements file not found: {self.requirements_file}")
            return False

        try:
            cmd = [
                sys.executable,
                "-m", "pip",
                "install",
                "-r", str(self.requirements_file)
            ]

            if self.verbose:
                logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info("✅ Dependencies installed successfully")
                self.results["requirements"] = True
                return True
            else:
                logger.error(f"❌ Installation failed:\n{result.stderr}")
                self.results["requirements"] = False
                return False

        except Exception as e:
            logger.error(f"❌ Installation error: {e}")
            self.results["requirements"] = False
            return False

    def check_requirements(self) -> bool:
        """Check if requirements are already installed"""
        logger.info("\n[2/5] Checking Python dependencies...")

        critical_packages = [
            "camoufox",
            "playwright",
            "ojd_daps_skills",
            "zen",
            "prefect",
            "plotly"
        ]

        all_installed = True
        for package in critical_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.info(f"  ✅ {package}")
            except ImportError:
                logger.warning(f"  ❌ {package} (not installed)")
                all_installed = False

        self.results["requirements"] = all_installed
        return all_installed

    def install_camoufox_binary(self) -> bool:
        """Download Camoufox browser binary"""
        logger.info("\n[3/5] Downloading Camoufox browser binary...")
        logger.info("  This may take 2-5 minutes (~150 MB download)")

        try:
            cmd = [sys.executable, "-m", "camoufox", "fetch"]

            if self.verbose:
                logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                logger.info("✅ Camoufox binary downloaded successfully")
                self.results["camoufox_binary"] = True
                return True
            else:
                logger.error(f"❌ Download failed:\n{result.stderr}")
                self.results["camoufox_binary"] = False
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Download timeout (10 minutes exceeded)")
            self.results["camoufox_binary"] = False
            return False
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            self.results["camoufox_binary"] = False
            return False

    def check_camoufox_binary(self) -> bool:
        """Check if Camoufox binary is installed"""
        logger.info("\n[3/5] Checking Camoufox browser binary...")

        try:
            from camoufox.sync_api import Camoufox
            logger.info("✅ Camoufox binary found")
            self.results["camoufox_binary"] = True
            return True
        except Exception as e:
            logger.warning(f"❌ Camoufox binary not found: {e}")
            logger.info("  Run: camoufox fetch")
            self.results["camoufox_binary"] = False
            return False

    def install_spacy_model(self) -> bool:
        """Download Spacy English language model"""
        logger.info("\n[4/5] Downloading Spacy language model...")

        try:
            cmd = [
                sys.executable,
                "-m", "spacy",
                "download",
                "en_core_web_sm"
            ]

            if self.verbose:
                logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("✅ Spacy model downloaded successfully")
                self.results["spacy_model"] = True
                return True
            else:
                logger.error(f"❌ Download failed:\n{result.stderr}")
                self.results["spacy_model"] = False
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Download timeout (5 minutes exceeded)")
            self.results["spacy_model"] = False
            return False
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            self.results["spacy_model"] = False
            return False

    def check_spacy_model(self) -> bool:
        """Check if Spacy model is installed"""
        logger.info("\n[4/5] Checking Spacy language model...")

        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            logger.info("✅ Spacy model found")
            self.results["spacy_model"] = True
            return True
        except Exception as e:
            logger.warning(f"❌ Spacy model not found: {e}")
            logger.info("  Run: python -m spacy download en_core_web_sm")
            self.results["spacy_model"] = False
            return False

    def check_tesseract_ocr(self) -> bool:
        """Check if Tesseract OCR is installed (manual install required)"""
        logger.info("\n[5/5] Checking Tesseract OCR...")

        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                logger.info(f"✅ Tesseract found: {version}")
                self.results["tesseract_ocr"] = True
                return True
            else:
                self._print_tesseract_instructions()
                self.results["tesseract_ocr"] = False
                return False

        except FileNotFoundError:
            self._print_tesseract_instructions()
            self.results["tesseract_ocr"] = False
            return False

    def _print_tesseract_instructions(self):
        """Print manual Tesseract installation instructions"""
        logger.warning("❌ Tesseract OCR not found (manual installation required)")
        logger.info("\n  Windows Installation:")
        logger.info("    1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.info("    2. Install to: C:\\Program Files\\Tesseract-OCR")
        logger.info("    3. Add to PATH: C:\\Program Files\\Tesseract-OCR")
        logger.info("\n  Linux Installation:")
        logger.info("    sudo apt-get install tesseract-ocr")
        logger.info("\n  macOS Installation:")
        logger.info("    brew install tesseract")

    def validate_installations(self) -> bool:
        """Validate all installations are working"""
        logger.info("\n" + "=" * 60)
        logger.info("Validating Installations")
        logger.info("=" * 60)

        all_valid = True

        # Test Camoufox import
        logger.info("\nTesting Camoufox...")
        try:
            from camoufox.sync_api import Camoufox
            logger.info("✅ Camoufox import successful")
        except Exception as e:
            logger.error(f"❌ Camoufox import failed: {e}")
            all_valid = False

        # Test Skills Extractor import
        logger.info("\nTesting Skills Extractor...")
        try:
            from ojd_daps_skills import SkillsExtractor
            logger.info("✅ Skills Extractor import successful")
        except Exception as e:
            logger.error(f"❌ Skills Extractor import failed: {e}")
            all_valid = False

        # Test custom services
        logger.info("\nTesting custom services...")
        try:
            sys.path.insert(0, str(self.backend_root))
            from app.services.anti_detection.camoufox_browser import (
                CamoufoxBrowserManager
            )
            from app.services.intelligence.skill_extraction_service import (
                IntelligentSkillMatcher
            )
            logger.info("✅ Custom services import successful")
        except Exception as e:
            logger.error(f"❌ Custom services import failed: {e}")
            all_valid = False

        return all_valid

    def print_summary(self):
        """Print installation summary"""
        logger.info("\n" + "=" * 60)
        logger.info("Installation Summary")
        logger.info("=" * 60)

        for component, status in self.results.items():
            icon = "✅" if status else "❌"
            logger.info(f"{icon} {component.replace('_', ' ').title()}")

        total = len(self.results)
        passed = sum(self.results.values())

        logger.info("\n" + "=" * 60)
        logger.info(f"Results: {passed}/{total} components ready")
        logger.info("=" * 60)

        if passed == total:
            logger.info("\n✅ Phase 1 installation COMPLETE!")
            logger.info("\nNext steps:")
            logger.info("  1. Review: PHASE1_IMPLEMENTATION_GUIDE.md")
            logger.info("  2. Test integration examples")
            logger.info("  3. Proceed to Phase 2")
        else:
            logger.warning("\n⚠️  Some components require manual installation")
            logger.info("\nRefer to PHASE1_IMPLEMENTATION_GUIDE.md for troubleshooting")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Autohire V2.0 Phase 1 Setup"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check installations, don't install anything"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    installer = Phase1Installer(
        check_only=args.check_only,
        verbose=args.verbose
    )

    success = installer.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
