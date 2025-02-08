# Finnish Wikipedia Statistics Generator

Simple script to generate statistics about the most viewed articles on Finnish Wikipedia. Creates formatted wiki markup tables that can be directly used on Wikipedia pages.

## Setup

1. Install Python 3
2. Install required packages:
```bash
pip install requests pandas
```
3. Download `wikistats.py`

## Usage

1. Open terminal/command prompt in the folder where `wikistats.py` is located
2. Run the script:
```bash
python wikistats.py
```
3. Follow the prompts:
   - Enter year (e.g., 2024)
   - Choose between whole year (1) or single month (2)
   - If choosing single month, enter month number (1-12)

## Output

The script creates a folder structure:
```
[year]/
  ├── kuukaudet/
  │   ├── 01_tammikuu_[year].txt
  │   ├── 02_helmikuu_[year].txt
  │   └── ...
  └── koko_vuosi_[year].txt
```

Each text file contains wiki markup that can be directly copied to Wikipedia.
