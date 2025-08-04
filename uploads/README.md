# Uploads Directory

This directory stores uploaded files for tickets.

## Security Notes

- Files are sanitized and renamed for security
- File types are restricted (see ALLOWED_EXTENSIONS in config)
- File size is limited (16MB by default)
- Original filenames are preserved in the database

## Directory Structure

Uploaded files are stored with sanitized names in the format:
`original_name_[8-char-hash].ext`

This directory should be:
- Writable by the web server
- Backed up regularly
- Protected from direct web access (if serving files, implement proper access controls)