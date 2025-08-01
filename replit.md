# Aircraft Systems Threat Simulator

## Overview

The Aircraft Systems Threat Simulator is a comprehensive cybersecurity training application designed to simulate potential cyber threats to aircraft systems. It provides real-time monitoring of multiple aircraft simultaneously, including critical systems like ADS-B (Automatic Dependent Surveillance-Broadcast), flight controls, and communications. The simulator supports both individual aircraft analysis and fleet-wide monitoring, allowing users to observe system states, simulate sophisticated cyber attacks, deploy defense mechanisms, and analyze threat patterns across multiple aircraft in a controlled environment for educational and training purposes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web-based Interface**: Single-page application using vanilla JavaScript with Bootstrap for responsive UI components
- **Real-time Updates**: Client-side polling mechanism that updates system status every 2 seconds
- **Dark Theme**: Aviation-themed dark UI with status indicators and visual alerts for compromised systems
- **Component Structure**: Modular card-based layout for different aircraft systems (ADS-B, Flight Control, Communications)

### Backend Architecture
- **Flask Framework**: Lightweight Python web framework serving as the application server
- **In-memory State Management**: System states and threat logs stored in Python dictionaries for simplicity
- **RESTful API Design**: JSON-based API endpoints for system status updates and threat simulation
- **Stateless Architecture**: No persistent sessions, with all state maintained server-side in memory

### Data Storage
- **Temporary Storage**: All system states and threat logs are stored in memory using Python data structures
- **No Database**: Simple dictionary-based storage for aircraft system parameters (position, altitude, speed, control surfaces)
- **Ephemeral Data**: System resets clear all stored information, making it suitable for training scenarios

### System Monitoring Components
- **ADS-B System Tracking**: Simulates GPS position, altitude, heading, and speed data
- **Flight Control Monitoring**: Tracks control surface positions (aileron, elevator, rudder) and throttle settings
- **Communications System**: Monitors radio frequency, signal strength, and message logs
- **Threat Detection**: Compromise flags and status indicators for each system component
- **Defense Systems**: Intrusion detection, data validation, encryption, and backup systems with real-time monitoring

## Attack Vectors
- **Basic Attacks**: Location/altitude spoofing, control input jamming/freezing, message injection, radio jamming
- **Advanced Attacks**: Man-in-the-middle attacks on all systems, replay attacks using old data/commands
- **Sophisticated Threats**: Multi-vector attacks targeting communication protocols and control systems

## Defense Mechanisms
- **Intrusion Detection System**: Monitors for unauthorized access and suspicious activities
- **Data Validation**: Verifies integrity of incoming data from aircraft systems
- **Encryption System**: Protects communications with automatic key rotation capabilities
- **Backup Systems**: Redundant systems that activate when primary systems are compromised
- **Emergency Countermeasures**: Manual override protocols including system isolation and backup navigation

## Multi-Aircraft Fleet Management
- **Fleet Overview**: Real-time monitoring dashboard showing status of all aircraft simultaneously
- **Individual Aircraft Selection**: Detailed system analysis and control for specific aircraft
- **Cross-Fleet Threat Analysis**: Centralized threat logging and analysis across entire fleet
- **Aircraft Fleet**: AAL123 (Boeing 737), UAL456 (Airbus A320), DLH789 (Boeing 777)
- **Scalable Architecture**: Support for monitoring and attacking multiple aircraft with independent system states

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for aviation-themed interface elements
- **CDN Delivery**: All frontend dependencies loaded via CDN for simplified deployment

### Python Dependencies
- **Flask**: Core web framework for serving the application
- **Standard Library**: Uses only Python built-in modules (os, json, datetime, logging) for simplicity

### Development Environment
- **Replit Integration**: Configured for Replit environment with appropriate entry points
- **Environment Variables**: Session secret key configurable via environment variables
- **Debug Logging**: Built-in logging configuration for development and troubleshooting