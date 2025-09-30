import os
import zipfile
import xml.etree.ElementTree as ET
import subprocess

# === CONFIGURATION ===
input_list_file = "examples/speakeasy.conf"         # File with one .mscz path per line
output_dir = "build/output_pdfs"             # Where PDFs will be saved
latex_file = "build/scores_book.tex"         # Output LaTeX file
mscore_cmd = "mscore"                  # MuseScore CLI command (adjust if needed)

# === SETUP ===
os.makedirs(output_dir, exist_ok=True)
pdf_entries = []

# === STEP 1: Read file paths ===
with open(input_list_file, "r") as f:
    score_paths = [line.strip() for line in f if line.strip()]

# === STEP 2: Process each score ===
for score_path in score_paths:
    print(f"Processing: {score_path}")
    basename = os.path.basename(score_path)
    name_no_ext = os.path.splitext(basename)[0]
    temp_dir = f"build/temp_{name_no_ext}"
    os.makedirs(temp_dir, exist_ok=True)

    # Unzip .mscz
    with zipfile.ZipFile(score_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Find .mscx file
    mscx_files = [f for f in os.listdir(temp_dir) if f.endswith(".mscx")]
    if len(mscx_files) != 1:
        print(f"⚠️ Skipping {score_path}: expected one .mscx file, found {len(mscx_files)}")
        continue

    mscx_path = os.path.join(temp_dir, mscx_files[0])

    # Parse title
    tree = ET.parse(mscx_path)
    root = tree.getroot()
    title = None
    for tag in root.findall(".//metaTag"):
        if tag.attrib.get("name") == "workTitle":
            title = tag.text
            break
    if not title:
        title = name_no_ext  # fallback

    # Export PDF
    pdf_path = os.path.join(output_dir, f"{name_no_ext}.pdf")
    subprocess.run([mscore_cmd, score_path, "-o", pdf_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Add to LaTeX list
    pdf_entries.append((title, pdf_path))

# === STEP 3: Create LaTeX file ===
with open(latex_file, "w") as f:
    f.write(r"\documentclass{article}"+"\n")
    f.write(r"\usepackage{pdfpages}"+"\n")
    f.write(r"\usepackage{fancyhdr}"+"\n")
    f.write(r"\pagestyle{fancy}"+"\n")
    f.write(r"\fancyhf{}"+"\n")
    f.write(r"\fancyfoot[C]{\thepage}"+"\n")
    f.write(r"\setlength{\footskip}{80pt}"+"\n")
    f.write(r"\usepackage{tocloft}"+"\n")
    f.write(r"\begin{document}"+"\n")
    f.write(r"\tableofcontents"+"\n")

    for title, pdf in pdf_entries:
        f.write(f"\\includepdf[\n")
        f.write("  pages=-,\n")
        f.write("  pagecommand={%\n")
        f.write(r"    \thispagestyle{plain}%" + "\n")
        f.write(r"    \phantomsection%" + "\n")
        f.write(r"    \addcontentsline{toc}{section}{\protect\numberline{}"+title+"}%" + "\n")
        f.write("  }\n")
        f.write("]{"+pdf+"}\n\n")

    f.write(r"\end{document}" + "\n")

print(f"\nGenerating PDF")
subprocess.run(["pdflatex", "--output-directory=build", latex_file],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["pdflatex", "--output-directory=build", latex_file],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"\nDone")
