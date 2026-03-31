import subprocess
import sys
import pkg_resources
import os
import ast
import glob

# Install nbformat if not already installed
try:
    import nbformat
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nbformat"])
    import nbformat

# Function to check if GPU is available


def check_gpu_available():
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False


def extract_imports_from_python_file(file_path):
    """Extract imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        tree = ast.parse(content)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        return imports
    except Exception as e:
        print(f"Error extracting imports from {file_path}: {e}")
        return set()


def extract_imports_from_notebook(file_path):
    """Extract imports from a Jupyter notebook."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            notebook = nbformat.read(file, as_version=4)

        imports = set()
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                try:
                    tree = ast.parse(cell.source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports.add(name.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
                except:
                    # Skip cells that can't be parsed
                    pass

        return imports
    except Exception as e:
        print(f"Error extracting imports from {file_path}: {e}")
        return set()


def map_import_to_package(import_name):
    """Map import name to package name."""
    # This is a simplified mapping for common packages
    mapping = {
        # Data processing and scientific computing
        'numpy': 'numpy',
        'np': 'numpy',
        'pandas': 'pandas',
        'pd': 'pandas',
        'scipy': 'scipy',
        'sympy': 'sympy',
        'numba': 'numba',
        'numexpr': 'numexpr',
        'dask': 'dask',
        'xarray': 'xarray',

        # Machine learning
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'lightgbm': 'lightgbm',
        'catboost': 'catboost',
        'imblearn': 'imbalanced-learn',
        'skimage': 'scikit-image',
        'skopt': 'scikit-optimize',

        # Deep learning
        'tensorflow': 'tensorflow',
        'tf': 'tensorflow',
        'keras': 'keras',
        'torch': 'torch',
        'pytorch_lightning': 'pytorch-lightning',
        'transformers': 'transformers',
        'fastai': 'fastai',
        'theano': 'theano',

        # Visualization
        'matplotlib': 'matplotlib',
        'plt': 'matplotlib',
        'mpl_toolkits': 'matplotlib',
        'seaborn': 'seaborn',
        'sns': 'seaborn',
        'plotly': 'plotly',
        'bokeh': 'bokeh',
        'altair': 'altair',
        'holoviews': 'holoviews',
        'pydeck': 'pydeck',
        'folium': 'folium',
        'wordcloud': 'wordcloud',
        'pygal': 'pygal',

        # NLP
        'nltk': 'nltk',
        'spacy': 'spacy',
        'gensim': 'gensim',
        'sastrawi': 'sastrawi',
        'textblob': 'textblob',
        'vader': 'vaderSentiment',
        'stanza': 'stanza',
        'allennlp': 'allennlp',
        'flair': 'flair',

        # Image processing
        'PIL': 'pillow',
        'Image': 'pillow',
        'cv2': 'opencv-python',
        'imageio': 'imageio',
        'scikit-image': 'scikit-image',

        # Web development/scraping
        'streamlit': 'streamlit',
        'st': 'streamlit',
        'flask': 'flask',
        'dash': 'dash',
        'django': 'django',
        'fastapi': 'fastapi',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'selenium': 'selenium',
        'scrapy': 'scrapy',
        'urllib': 'urllib3',

        # Utilities
        'json': 'jsonlib',
        'yaml': 'pyyaml',
        'joblib': 'joblib',
        'tqdm': 'tqdm',
        're': 'regex',
        'os': None,  # Standard library
        'sys': None,  # Standard library
        'time': None,  # Standard library
        'datetime': None,  # Standard library
        'pathlib': None,  # Standard library

        # Database
        'sqlalchemy': 'sqlalchemy',
        'sqlite3': None,  # Standard library
        'pymongo': 'pymongo',
        'psycopg2': 'psycopg2',
        'mysql': 'mysql-connector-python',

        # Data structures and analysis
        'statsmodels': 'statsmodels',
        'networkx': 'networkx',
        'h5py': 'h5py',
        'openpyxl': 'openpyxl',
        'xlrd': 'xlrd',
        'xlwt': 'xlwt',
        'pyarrow': 'pyarrow',
        'polars': 'polars',
        'pydot': 'pydot',
        'graphviz': 'graphviz',

        # Geographic data
        'geopandas': 'geopandas',
        'shapely': 'shapely',
        'pyproj': 'pyproj',
        'geopy': 'geopy',
        'cartopy': 'cartopy',

        # Time series
        'prophet': 'prophet',
        'pmdarima': 'pmdarima',
        'arch': 'arch',
        'pywt': 'PyWavelets',

        # Other useful libraries
        'pytest': 'pytest',
        'hypothesis': 'hypothesis',
        'boto3': 'boto3',
        'awscli': 'awscli',
        'pyspark': 'pyspark',
        'gym': 'gym',
        'rich': 'rich',
    }
    return mapping.get(import_name, import_name)


def scan_directory_for_imports(directory='.', recursive=True):
    """Scan directory for Python files and Jupyter notebooks and extract imports."""
    imports = set()

    # Determine pattern based on recursion
    pattern = '**/*.py' if recursive else '*.py'

    # Scan Python files
    for file_path in glob.glob(os.path.join(directory, pattern), recursive=recursive):
        imports.update(extract_imports_from_python_file(file_path))

    # Scan Jupyter notebooks
    pattern = '**/*.ipynb' if recursive else '*.ipynb'
    for file_path in glob.glob(os.path.join(directory, pattern), recursive=recursive):
        imports.update(extract_imports_from_notebook(file_path))

    # Map imports to package names
    packages = {map_import_to_package(import_name) for import_name in imports}

    # Filter out standard library modules
    try:
        import stdlib_list
        stdlib_modules = stdlib_list.stdlib_list()
        packages = {pkg for pkg in packages if pkg not in stdlib_modules}
    except ImportError:
        pass  # stdlib_list not installed, skip filtering

    return packages


def get_required_packages(scan_dir=None):
    """Get the list of required packages, optionally scanning directories."""
    packages = [
        'pandas',
        'sastrawi',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'nltk',
        'spacy',
        'gensim',
        'tqdm',
        'joblib',
        'streamlit',
        'nbformat',
        './id_nusantara-1.1.tar.gz',
    ]

    # If directory is provided, scan for imports
    if scan_dir:
        detected_packages = scan_directory_for_imports(scan_dir)
        print(
            f"Detected packages from imports: {', '.join(detected_packages)}")
        packages.extend(detected_packages)
        # Remove duplicates
        packages = list(set(packages))

    # Check if GPU is available and add appropriate TensorFlow version
    if check_gpu_available():
        packages.append('tensorflow[and-cuda]')  # For CUDA-enabled GPUs
        print("GPU detected! Will use TensorFlow with CUDA support.")
    else:
        packages.append('tensorflow')  # CPU-only version
        print("No GPU detected. Will use CPU-only TensorFlow.")

    return packages


REQUIRED_PACKAGES = []  # Will be initialized when needed


def check_packages(packages_list):
    """Check if all required packages are installed."""
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = [pkg for pkg in packages_list if pkg.lower() not in installed]
    return missing


def install_packages(packages):
    """Install missing packages."""
    for package in packages:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")


def generate_requirements_txt(packages_list):
    """Generate a requirements.txt file from the packages list."""
    with open('requirements.txt', 'w') as f:
        for package in packages_list:
            f.write(f"{package}\n")
    print("requirements.txt file generated successfully.")


if __name__ == "__main__":
    print("\nFeature Engineering Dependencies Manager")
    print("=======================================")
    print("1. Check and install missing packages from predefined list")
    print("2. Scan directory and install packages based on imports")
    print("3. Generate requirements.txt file")
    print("4. Scan specific file for imports and install packages")

    choice = input("\nEnter your choice (1/2/3/4): ")

    if choice == "1":
        REQUIRED_PACKAGES = get_required_packages()
        print("\nChecking for required packages...")
        missing_packages = check_packages(REQUIRED_PACKAGES)

        if missing_packages:
            print(f"Missing packages: {', '.join(missing_packages)}")
            install_choice = input(
                "Do you want to install missing packages? (y/n): ")
            if install_choice.lower() == 'y':
                install_packages(missing_packages)
                print("All packages installed successfully.")
            else:
                print("Packages not installed. Some features may not work properly.")
        else:
            print("All required packages are already installed.")

    elif choice == "2":
        directory = input(
            "Enter directory path to scan (default: current directory): ") or '.'
        recursive = input(
            "Scan recursively? (y/n, default: y): ").lower() != 'n'
        REQUIRED_PACKAGES = get_required_packages(scan_dir=directory)

        print("\nChecking for required packages...")
        missing_packages = check_packages(REQUIRED_PACKAGES)

        if missing_packages:
            print(f"Missing packages: {', '.join(missing_packages)}")
            install_choice = input(
                "Do you want to install missing packages? (y/n): ")
            if install_choice.lower() == 'y':
                install_packages(missing_packages)
                print("All packages installed successfully.")
            else:
                print("Packages not installed. Some features may not work properly.")
        else:
            print("All required packages are already installed.")

    elif choice == "3":
        REQUIRED_PACKAGES = get_required_packages()
        generate_requirements_txt(REQUIRED_PACKAGES)
        print("\nYou can now use the requirements.txt file for Streamlit deployment.")

    elif choice == "4":
        file_path = input("Enter file path to scan: ")
        if file_path.endswith('.py'):
            imports = extract_imports_from_python_file(file_path)
        elif file_path.endswith('.ipynb'):
            imports = extract_imports_from_notebook(file_path)
        else:
            print("Unsupported file type. Please provide a .py or .ipynb file.")
            sys.exit(1)

        packages = {map_import_to_package(import_name)
                    for import_name in imports}
        print(f"Detected packages: {', '.join(packages)}")

        install_choice = input(
            "Do you want to install these packages? (y/n): ")
        if install_choice.lower() == 'y':
            missing_packages = check_packages(packages)
            if missing_packages:
                install_packages(missing_packages)
                print("All packages installed successfully.")
            else:
                print("All required packages are already installed.")
    else:
        print("Invalid choice. Exiting.")
