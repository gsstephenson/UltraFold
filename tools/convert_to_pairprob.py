import math
import sys

def find_max_position(bps_file):
    max_position = 0
    with open(bps_file, 'r') as infile:
        for line in infile:
            # Only check the first column for each line
            position = int(line.strip().split()[0])
            max_position = max(max_position, position)
    return max_position

def convert_bpp2seq_to_pairprob(bps_file, pairprob_file):
    max_position = find_max_position(bps_file)
    
    with open(bps_file, 'r') as infile, open(pairprob_file, 'w') as outfile:
        # Write the header with the max position number
        outfile.write(f"{max_position}\n")
        outfile.write("i\tj\t-log10(Probability)\n")
        
        # Read the entire bpp2seq file line by line
        for line in infile:
            # Split the line into components
            parts = line.strip().split()
            position = parts[0]
            nucleotide = parts[1]
            bindings = parts[2:]
            
            # Process each binding information
            for binding in bindings:
                # Extract the position and probability
                bound_pos, prob_str = binding.split(':')
                prob = float(prob_str)
                
                # Calculate -log10(probability)
                if prob > 0:
                    log_prob = -math.log10(prob)
                    # Write to the output file in the format: i\tj\t-log10(Probability)
                    outfile.write(f"{position}\t{bound_pos}\t{log_prob:.5f}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_pairprob.py input_file output_file")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    convert_bpp2seq_to_pairprob(input_file, output_file)
