#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import platform
import shutil

class LettaInstallationVerifier:
    def __init__(self):
        self.checks = {
            'system_requirements': False,
            'docker_installed': False,
            'letta_server_running': False,
            'environment_configured': False,
            'required_dependencies': False
        }
        
        self.report = {
            'system_info': {},
            'docker_info': {},
            'letta_server_status': {},
            'dependencies': {}
        }
    
    def check_system_requirements(self):
        """
        Verify system meets basic requirements for Letta
        """
        self.report['system_info'] = {
            'os': platform.system(),
            'os_release': platform.release(),
            'python_version': platform.python_version(),
            'architecture': platform.machine()
        }
        
        # Python version check
        python_version = platform.python_version_tuple()
        if int(python_version[0]) >= 3 and int(python_version[1]) >= 9:
            self.checks['system_requirements'] = True
        
        return self.checks['system_requirements']
    
    def check_docker_installation(self):
        """
        Verify Docker is installed and running
        """
        try:
            # Check Docker installation
            docker_version = subprocess.check_output(['docker', '--version'], 
                                                     stderr=subprocess.STDOUT, 
                                                     text=True).strip()
            
            # Check Docker daemon status
            docker_info = subprocess.check_output(['docker', 'info'], 
                                                  stderr=subprocess.STDOUT, 
                                                  text=True)
            
            self.report['docker_info'] = {
                'version': docker_version,
                'status': 'Running'
            }
            
            self.checks['docker_installed'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.report['docker_info'] = {
                'version': 'Not Installed',
                'status': 'Not Running'
            }
            self.checks['docker_installed'] = False
        
        return self.checks['docker_installed']
    
    def check_letta_server(self):
        """
        Check if Letta server is running
        """
        try:
            # Default Letta server URL
            letta_url = os.getenv('LETTA_SERVER_URL', 'http://localhost:8283')
            
            # Use curl to check server response
            curl_result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', letta_url],
                capture_output=True, text=True, timeout=5
            )
            
            http_status = curl_result.stdout.strip()
            
            self.report['letta_server_status'] = {
                'url': letta_url,
                'http_status': http_status,
                'status': 'Running' if http_status in ['200', '204', '301', '302'] else 'Not Running'
            }
            
            self.checks['letta_server_running'] = http_status in ['200', '204', '301', '302']
        except Exception as e:
            self.report['letta_server_status'] = {
                'url': letta_url,
                'error': str(e),
                'status': 'Connection Failed'
            }
            self.checks['letta_server_running'] = False
        
        return self.checks['letta_server_running']
    
    def check_environment_configuration(self):
        """
        Verify Letta environment configuration
        """
        letta_env_path = os.path.expanduser('~/.letta/env')
        
        try:
            if os.path.exists(letta_env_path):
                with open(letta_env_path, 'r') as f:
                    env_content = f.read()
                
                required_vars = ['GEMINI_API_KEY', 'LETTA_SERVER_URL']
                self.checks['environment_configured'] = all(
                    var in env_content for var in required_vars
                )
                
                self.report['environment'] = {
                    'config_file': letta_env_path,
                    'required_vars_present': self.checks['environment_configured']
                }
            else:
                self.checks['environment_configured'] = False
                self.report['environment'] = {
                    'config_file': 'Not Found',
                    'required_vars_present': False
                }
        except Exception as e:
            self.checks['environment_configured'] = False
            self.report['environment'] = {
                'error': str(e),
                'required_vars_present': False
            }
        
        return self.checks['environment_configured']
    
    def check_dependencies(self):
        """
        Check required Python dependencies
        """
        required_deps = [
            'google-generativeai',
            'python-dotenv',
            'requests'
        ]
        
        try:
            import pkg_resources
            
            dep_status = {}
            for dep in required_deps:
                try:
                    pkg_resources.get_distribution(dep)
                    dep_status[dep] = 'Installed'
                except pkg_resources.DistributionNotFound:
                    dep_status[dep] = 'Not Installed'
            
            self.report['dependencies'] = dep_status
            
            self.checks['required_dependencies'] = all(
                status == 'Installed' for status in dep_status.values()
            )
        except Exception as e:
            self.report['dependencies'] = {
                'error': str(e)
            }
            self.checks['required_dependencies'] = False
        
        return self.checks['required_dependencies']
    
    def generate_report(self):
        """
        Generate a comprehensive installation verification report
        """
        print("🔍 Letta Installation Verification Report 🔍")
        print("==========================================")
        
        # Run all checks
        self.check_system_requirements()
        self.check_docker_installation()
        self.check_letta_server()
        self.check_environment_configuration()
        self.check_dependencies()
        
        # Print detailed report
        print("\n📋 Detailed System Information:")
        print(json.dumps(self.report['system_info'], indent=2))
        
        print("\n🐳 Docker Status:")
        print(json.dumps(self.report['docker_info'], indent=2))
        
        print("\n🌐 Letta Server Status:")
        print(json.dumps(self.report['letta_server_status'], indent=2))
        
        print("\n⚙️ Environment Configuration:")
        print(json.dumps(self.report['environment'], indent=2))
        
        print("\n📦 Dependencies:")
        print(json.dumps(self.report['dependencies'], indent=2))
        
        print("\n✅ Installation Checks Summary:")
        for check, status in self.checks.items():
            print(f"{check.replace('_', ' ').title()}: {'Passed' if status else 'Failed'}")
        
        # Overall status
        overall_status = all(self.checks.values())
        print(f"\nOverall Installation Status: {'✅ Successful' if overall_status else '❌ Incomplete'}")
        
        return overall_status

def main():
    verifier = LettaInstallationVerifier()
    verifier.generate_report()

if __name__ == '__main__':
    main()
