#!/usr/bin/env python3
"""
Enhanced Autohire Deployment Validation Script
Validates the complete infrastructure and tests all components.
"""

import asyncio
import json
import subprocess
import time
import sys
import os
from typing import Dict, List, Any
import httpx


class DeploymentValidator:
    def __init__(self):
        self.results = []
        self.failed_checks = []

    def log_result(self, check_name: str, success: bool, details: str = ""):
        """Log validation result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {check_name}"
        if details:
            result += f" - {details}"

        print(result)
        self.results.append({
            "check": check_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })

        if not success:
            self.failed_checks.append(check_name)

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        print("\n🔍 Checking Prerequisites...")

        # Check Python
        try:
            python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
            self.log_result("Python Installation", True, python_version)
        except Exception as e:
            self.log_result("Python Installation", False, str(e))
            return False

        # Check Docker
        try:
            docker_version = subprocess.check_output(["docker", "--version"], text=True).strip()
            self.log_result("Docker Installation", True, docker_version)
        except Exception as e:
            self.log_result("Docker Installation", False, "Docker not found - required for full deployment")

        # Check Docker Compose
        try:
            compose_version = subprocess.check_output(["docker-compose", "--version"], text=True).strip()
            self.log_result("Docker Compose Installation", True, compose_version)
        except Exception as e:
            self.log_result("Docker Compose Installation", False, "Docker Compose not found")

        # Check Node.js
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            self.log_result("Node.js Installation", True, node_version)
        except Exception as e:
            self.log_result("Node.js Installation", False, "Node.js not found - required for frontend")

        return len(self.failed_checks) == 0

    def validate_project_structure(self) -> bool:
        """Validate project file structure"""
        print("\n📁 Validating Project Structure...")

        required_files = [
            "backend/enhanced_autohire_backend.py",
            "backend/requirements.txt",
            "backend/Dockerfile.enhanced",
            "docker-compose.enhanced.yml",
            "monitoring/prometheus/prometheus.yml",
            ".github/workflows/ci-cd-enhanced.yml"
        ]

        all_present = True
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_result(f"File: {file_path}", True)
            else:
                self.log_result(f"File: {file_path}", False, "Missing")
                all_present = False

        return all_present

    async def test_backend_core(self) -> bool:
        """Test basic backend functionality"""
        print("\n🖥️ Testing Backend Core Functionality...")

        # Test if we can import core modules
        try:
            sys.path.append("backend")
            import fastapi
            self.log_result("FastAPI Import", True, f"Version {fastapi.__version__}")
        except Exception as e:
            self.log_result("FastAPI Import", False, str(e))
            return False

        try:
            import playwright
            self.log_result("Playwright Import", True, f"Available")
        except Exception as e:
            self.log_result("Playwright Import", False, "Install with: pip install playwright && playwright install")

        return True

    async def test_api_endpoints(self, base_url: str = "http://localhost:8002") -> bool:
        """Test API endpoints if backend is running"""
        print(f"\n🌐 Testing API Endpoints at {base_url}...")

        endpoints_to_test = [
            ("/health", "GET"),
            ("/metrics", "GET"),
            ("/api/v1/browser/capabilities", "GET")
        ]

        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, method in endpoints_to_test:
                try:
                    if method == "GET":
                        response = await client.get(f"{base_url}{endpoint}")

                    if response.status_code == 200:
                        self.log_result(f"API {method} {endpoint}", True, f"Status: {response.status_code}")
                    else:
                        self.log_result(f"API {method} {endpoint}", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_result(f"API {method} {endpoint}", False, f"Connection failed: {str(e)}")

        return True

    def test_docker_setup(self) -> bool:
        """Test Docker configuration"""
        print("\n🐳 Testing Docker Configuration...")

        # Check if docker-compose.enhanced.yml is valid
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.enhanced.yml", "config"],
                capture_output=True,
                text=True,
                cwd="."
            )

            if result.returncode == 0:
                self.log_result("Docker Compose Config", True, "Configuration valid")
            else:
                self.log_result("Docker Compose Config", False, result.stderr)
                return False
        except Exception as e:
            self.log_result("Docker Compose Config", False, str(e))
            return False

        return True

    def validate_ci_cd_setup(self) -> bool:
        """Validate CI/CD configuration"""
        print("\n🔄 Validating CI/CD Setup...")

        github_workflows_path = ".github/workflows/ci-cd-enhanced.yml"
        if os.path.exists(github_workflows_path):
            self.log_result("GitHub Actions Workflow", True, "ci-cd-enhanced.yml present")

            # Check workflow syntax
            try:
                import yaml
                with open(github_workflows_path, 'r') as f:
                    workflow = yaml.safe_load(f)

                required_jobs = ['test-backend', 'test-frontend', 'security-scan', 'build-backend', 'build-frontend']
                for job in required_jobs:
                    if job in workflow.get('jobs', {}):
                        self.log_result(f"CI/CD Job: {job}", True)
                    else:
                        self.log_result(f"CI/CD Job: {job}", False, "Job missing")

            except Exception as e:
                self.log_result("GitHub Workflow Validation", False, str(e))
        else:
            self.log_result("GitHub Actions Workflow", False, "Workflow file missing")

        return True

    def validate_monitoring_setup(self) -> bool:
        """Validate monitoring configuration"""
        print("\n📊 Validating Monitoring Setup...")

        prometheus_config = "monitoring/prometheus/prometheus.yml"
        if os.path.exists(prometheus_config):
            self.log_result("Prometheus Config", True, "prometheus.yml present")
        else:
            self.log_result("Prometheus Config", False, "prometheus.yml missing")

        # Check if Grafana dashboards directory exists
        grafana_dashboards = "monitoring/grafana/dashboards"
        if os.path.exists(grafana_dashboards):
            self.log_result("Grafana Dashboards", True, "Directory present")
        else:
            self.log_result("Grafana Dashboards", False, "Create dashboards directory")

        return True

    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r['success'])
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        report = {
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": len(self.failed_checks),
                "success_rate": round(success_rate, 2),
                "overall_status": "READY" if success_rate >= 80 else "NEEDS_ATTENTION"
            },
            "failed_checks": self.failed_checks,
            "detailed_results": self.results,
            "recommendations": self.get_recommendations()
        }

        return report

    def get_recommendations(self) -> List[str]:
        """Get deployment recommendations based on results"""
        recommendations = []

        if "Docker Installation" in self.failed_checks:
            recommendations.append("Install Docker Desktop from https://www.docker.com/products/docker-desktop")

        if "Node.js Installation" in self.failed_checks:
            recommendations.append("Install Node.js from https://nodejs.org/")

        if "Playwright Import" in self.failed_checks:
            recommendations.append("Install Playwright: pip install playwright && playwright install")

        if any("API" in check for check in self.failed_checks):
            recommendations.append("Start the backend server to test API endpoints")

        if len(self.failed_checks) == 0:
            recommendations.append("🎉 All checks passed! Ready for production deployment")
            recommendations.append("Run: docker-compose -f docker-compose.enhanced.yml up -d")
            recommendations.append("Access Grafana at http://localhost:3001")
            recommendations.append("Access Prometheus at http://localhost:9090")

        return recommendations

    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete deployment validation"""
        print("🚀 Starting Enhanced Autohire Deployment Validation")
        print("=" * 60)

        # Run all validation steps
        await asyncio.gather(
            asyncio.to_thread(self.check_prerequisites),
            asyncio.to_thread(self.validate_project_structure),
            self.test_backend_core(),
            asyncio.to_thread(self.test_docker_setup),
            asyncio.to_thread(self.validate_ci_cd_setup),
            asyncio.to_thread(self.validate_monitoring_setup)
        )

        # Test API endpoints (optional - only if backend is running)
        try:
            await self.test_api_endpoints()
        except Exception:
            self.log_result("API Endpoint Testing", False, "Backend not running - skip for now")

        # Generate final report
        report = self.generate_deployment_report()

        print("\n" + "=" * 60)
        print("📋 DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {report['summary']['passed_checks']}")
        print(f"❌ Failed: {report['summary']['failed_checks']}")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"🎯 Overall Status: {report['summary']['overall_status']}")

        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")

        # Save detailed report
        with open("deployment_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: deployment_validation_report.json")
        return report


async def main():
    """Main validation function"""
    validator = DeploymentValidator()
    report = await validator.run_full_validation()

    # Exit with appropriate code
    if report['summary']['overall_status'] == "READY":
        print("\n🎉 Deployment validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Deployment needs attention. Please address the failed checks.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())