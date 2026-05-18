import re
import sys

def update_openapi(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find paths and their methods
    # This is a bit complex for regex but since the structure is consistent we can try
    
    lines = content.split('\n')
    new_lines = []
    current_path = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Match path: "  /api/...:"
        path_match = re.match(r'^  (/api/[^:]+):', line)
        if path_match:
            current_path = path_match.group(1)
            new_lines.append(line)
            i += 1
            continue
            
        # Match method: "    post:" or "    get:"
        method_match = re.match(r'^    (post|get|put|delete|patch):', line)
        if method_match and current_path:
            new_lines.append(line)
            i += 1
            # Look for x-google-backend in the next few lines
            while i < len(lines) and not re.match(r'^    (post|get|put|delete|patch|parameters|responses):', lines[i]) and not re.match(r'^  /', lines[i]):
                inner_line = lines[i]
                if 'x-google-backend:' in inner_line:
                    new_lines.append(inner_line)
                    i += 1
                    # Next line should be address
                    if i < len(lines) and 'address:' in lines[i]:
                        address_line = lines[i]
                        # Extract the base URL (e.g., COURSE_SERVICE_URL)
                        # Address line format: "        address: \"COURSE_SERVICE_URL\""
                        m = re.search(r'address:\s*"([^"]+)"', address_line)
                        if m:
                            base_url = m.group(1)
                            # Ensure we don't append path if it's already there (though the task says to add it)
                            # The task says: "COURSE_SERVICE_URL" -> "COURSE_SERVICE_URL/api/courses"
                            new_address = f'{base_url}{current_path}'
                            indent = re.match(r'^(\s+)', address_line).group(1)
                            new_lines.append(f'{indent}address: "{new_address}"')
                            new_lines.append(f'{indent}path_translation: CONSTANT_ADDRESS')
                            i += 1
                        else:
                            new_lines.append(inner_line) # Should not happen based on provided content
                    continue
                
                # Check if we are still inside the same operation
                if re.match(r'^  ', inner_line) and not re.match(r'^    ', inner_line):
                    break
                
                new_lines.append(inner_line)
                i += 1
            continue
            
        new_lines.append(line)
        i += 1

    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))

if __name__ == "__main__":
    update_openapi(sys.argv[1])
