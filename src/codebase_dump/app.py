import argparse
import sys
import os

from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager
from codebase_dump.core.codebase_analysis import CodebaseAnalysis
from codebase_dump.core.audit_api_uploader import AuditApiUploader
from codebase_dump.core.output_formatter import OutputFormatterBase, MarkdownOutputFormatter, PlainTextOutputFormatter


def main():
    parser = argparse.ArgumentParser(
        description="Generate a single-file dump of your repository, so you can use it as LLM input.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("path", nargs="?", help="Path to the directory to analyze")
    parser.add_argument("--max-size", type=int, default=10240, help="Maximum allowed text content size in KB (default: 10240 KB)")
    parser.add_argument("-o", "--output-format", choices=["text", "markdown"], default="text", help="Output format (default: text)")
    parser.add_argument("-f", "--file", help="Output file name (default: <directory_name>_codebase_dump.<format_extension>)")
    parser.add_argument("--audit-upload", help="Send the output to the audits API", action="store_true")
    parser.add_argument("--audit-base-url", default="https://codeaudits.ai/", help="API URL to send the audit to (default: https://codeaudits.ai/)")
    parser.add_argument("--ignore-top-large-files", type=int, default=0, help="Number of largest files to ignore (default: 0)")
    parser.add_argument("--api-key", type=str, default=None, help="Your private API key to assign submitted repository to your account on https://codeaudits.ai/")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if not args.path:
        print("Error: Path argument is required.")
        parser.print_help(sys.stderr)
        sys.exit(1)

    ignore_patterns_manager = IgnorePatternManager(args.path)
    codebase_analysis = CodebaseAnalysis()

    print("Codebase Digest")
    print("Analyzing directory: " + args.path)
    
    data = codebase_analysis.analyze_directory(path=args.path, 
                                               ignore_patterns_manager=ignore_patterns_manager, 
                                               base_path=args.path, 
                                               ignore_top_files=args.ignore_top_large_files)
    
    total_size = data.size
    estimated_output_size = data.get_non_ignored_text_content_size()
    estimated_output_size += len(data.get_all_non_ignored_files()) * 100  # Assume 100 bytes per file for structure
    estimated_output_size += 1000  # Add 1KB for summary
    print(f"Estimated output size: {estimated_output_size / 1024:.2f} KB")
    if estimated_output_size / 1024 > args.max_size:
        print(f"\nWarning: The estimated output size ({estimated_output_size / 1024:.2f} KB) exceeds the maximum allowed size ({args.max_size} KB).")
    elif total_size / 1024 > args.max_size * 2:  # Only show this if total size is significantly larger
        print(f"\nNote: The total size of all text files in the directory ({total_size / 1024:.2f} KB) is significantly larger than the estimated output size.")
        print("This is likely due to large files or directories that will be ignored in the analysis.")

    output_formatter: OutputFormatterBase = None
    if args.output_format == "markdown":
        output_formatter = MarkdownOutputFormatter()
    else:
        output_formatter = PlainTextOutputFormatter()

    output = output_formatter.format(data, ignore_patterns_manager.ignore_patterns_as_str)

    # Save the output to a file
    file_name = args.file or f"{os.path.basename(args.path)}_codebase_dump{output_formatter.output_file_extension()}"
    full_path = os.path.abspath(file_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\nAnalysis saved to: {full_path}")
    
    print("Analysis Summary\n")
    print(output_formatter.generate_tree_string(data, show_ignored=False))
    print(output_formatter.generate_summary_string(data))
    print("Ignore summary:\n")
    print(output_formatter.generate_ignored_files_summary(data, ignore_patterns_manager.ignore_patterns_as_str))

    try:
        from codebase_dump._version import __version__ as app_version
    except ImportError:
        app_version = None

    submitted_by = f"codebase-dump-v{app_version}" if app_version else "codebase-dump"
    if args.audit_upload:
        audit_api_uploader = AuditApiUploader(
            api_key=args.api_key,
            api_url=args.audit_base_url,
            api_submitted_by=submitted_by
        )
        audit_api_uploader.upload_audit(output)

if __name__ == "__main__":
    main()