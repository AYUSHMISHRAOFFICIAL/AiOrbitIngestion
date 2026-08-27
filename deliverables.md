# Deliverables Verification

## 1. Project Structure
```text
Folder PATH listing for volume OS
Volume serial number is 00000030 8C21:61B4
C:.
|   .env
|   .env.example
|   .gitignore
|   audit.py
|   counts.py
|   diagnostic.py
|   find_tools.py
|   get_tools.py
|   README.md
|   requirements.txt
|   run.py
|   verify.py
|   
+---.pytest_cache
|   |   .gitignore
|   |   CACHEDIR.TAG
|   |   README.md
|   |   
|   \---v
|       \---cache
|               lastfailed
|               nodeids
|               
+---data
|   +---final
|   |       entities.json
|   |       relationships.json
|   |       
|   +---processed
|   \---raw
+---src
|   |   config.py
|   |   io.py
|   |   relationships.py
|   |   resolution.py
|   |   schema.py
|   |   __init__.py
|   |   
|   +---processing
|   |   |   classification.py
|   |   |   cleaning.py
|   |   |   filtering.py
|   |   |   normalization.py
|   |   |   __init__.py
|   |   |   
|   |   \---__pycache__
|   |           classification.cpython-311.pyc
|   |           cleaning.cpython-311.pyc
|   |           filtering.cpython-311.pyc
|   |           normalization.cpython-311.pyc
|   |           __init__.cpython-311.pyc
|   |           
|   +---sources
|   |   |   github.py
|   |   |   http_client.py
|   |   |   huggingface.py
|   |   |   rss.py
|   |   |   youtube.py
|   |   |   __init__.py
|   |   |   
|   |   \---__pycache__
|   |           github.cpython-311.pyc
|   |           http_client.cpython-311.pyc
|   |           huggingface.cpython-311.pyc
|   |           rss.cpython-311.pyc
|   |           youtube.cpython-311.pyc
|   |           __init__.cpython-311.pyc
|   |           
|   \---__pycache__
|           config.cpython-311.pyc
|           io.cpython-311.pyc
|           relationships.cpython-311.pyc
|           resolution.cpython-311.pyc
|           schema.cpython-311.pyc
|           __init__.cpython-311.pyc
|           
\---tests
    |   test_adapters.py
    |   test_filtering.py
    |   test_http_client.py
    |   test_io.py
    |   test_pipeline.py
    |   test_resolution.py
    |   
    \---__pycache__
            test_adapters.cpython-311-pytest-9.1.1.pyc
            test_filtering.cpython-311-pytest-9.1.1.pyc
            test_http_client.cpython-311-pytest-9.1.1.pyc
            test_io.cpython-311-pytest-9.1.1.pyc
            test_pipeline.cpython-311-pytest-9.1.1.pyc
            test_resolution.cpython-311-pytest-9.1.1.pyc
```

## 2. Check Paths
```text
Test-Path src: True
Test-Path data: True
Test-Path run.py: True
Test-Path README.md: True
```

## 3. Inspect src/
```text
C:\Users\AyushM\Desktop\InternshipTask\src\processing
C:\Users\AyushM\Desktop\InternshipTask\src\sources
C:\Users\AyushM\Desktop\InternshipTask\src\__pycache__
C:\Users\AyushM\Desktop\InternshipTask\src\config.py
C:\Users\AyushM\Desktop\InternshipTask\src\io.py
C:\Users\AyushM\Desktop\InternshipTask\src\relationships.py
C:\Users\AyushM\Desktop\InternshipTask\src\resolution.py
C:\Users\AyushM\Desktop\InternshipTask\src\schema.py
C:\Users\AyushM\Desktop\InternshipTask\src\__init__.py
C:\Users\AyushM\Desktop\InternshipTask\src\processing\__pycache__
C:\Users\AyushM\Desktop\InternshipTask\src\processing\classification.py
C:\Users\AyushM\Desktop\InternshipTask\src\processing\cleaning.py
C:\Users\AyushM\Desktop\InternshipTask\src\processing\filtering.py
C:\Users\AyushM\Desktop\InternshipTask\src\processing\normalization.py
C:\Users\AyushM\Desktop\InternshipTask\src\processing\__init__.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\__pycache__
C:\Users\AyushM\Desktop\InternshipTask\src\sources\github.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\http_client.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\huggingface.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\rss.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\youtube.py
C:\Users\AyushM\Desktop\InternshipTask\src\sources\__init__.py
```

## 4. Inspect data/
```text
C:\Users\AyushM\Desktop\InternshipTask\data\final
C:\Users\AyushM\Desktop\InternshipTask\data\processed
C:\Users\AyushM\Desktop\InternshipTask\data\raw
C:\Users\AyushM\Desktop\InternshipTask\data\final\entities.json
C:\Users\AyushM\Desktop\InternshipTask\data\final\relationships.json
```

## 5. Verify the final JSON files actually exist
```text
C:\Users\AyushM\Desktop\InternshipTask\data\final\entities.json
C:\Users\AyushM\Desktop\InternshipTask\data\final\relationships.json
```

## 6. Verify run.py and README
```text
C:\Users\AyushM\Desktop\InternshipTask\run.py
C:\Users\AyushM\Desktop\InternshipTask\README.md
```

## 7. Git status
```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## 8. Check the committed final structure
```text
.env.example
.gitignore
README.md
audit.py
counts.py
data/final/entities.json
data/final/relationships.json
diagnostic.py
find_tools.py
get_tools.py
requirements.txt
run.py
src/__init__.py
src/config.py
src/io.py
src/processing/__init__.py
src/processing/classification.py
src/processing/cleaning.py
src/processing/filtering.py
src/processing/normalization.py
src/relationships.py
src/resolution.py
src/schema.py
src/sources/__init__.py
src/sources/github.py
src/sources/http_client.py
src/sources/huggingface.py
src/sources/rss.py
src/sources/youtube.py
tests/test_adapters.py
tests/test_filtering.py
tests/test_http_client.py
tests/test_io.py
tests/test_pipeline.py
tests/test_resolution.py
verify.py
```
