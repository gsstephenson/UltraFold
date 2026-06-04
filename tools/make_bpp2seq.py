import pandas as pd
import sys

def create_bpp2seq(profile_file, output_file):
    # Read the profile.txt file
    df = pd.read_csv(profile_file, sep='\t')

    # Extract the necessary columns
    df_bpp2seq = pd.DataFrame()
    df_bpp2seq['Position'] = df['Nucleotide']  # First column: nucleotide position
    df_bpp2seq['Nucleotide'] = df['Sequence']  # Second column: type of nucleotide
    df_bpp2seq['Label'] = 'e1'  # Third column: write "e1"
    
    # Replace NaN in Norm_profile with -1 and extract the Norm_profile column
    df_bpp2seq['Norm_profile'] = df['Norm_profile'].fillna(-999)  # Fourth column: Norm_profile, replacing NaN with -1

    # Save the result to a .bpp2seq file
    df_bpp2seq.to_csv(output_file, sep='\t', header=False, index=False)

if __name__ == "__main__":
    # Command line arguments: input_file and output_file
    if len(sys.argv) != 3:
        print("Usage: python make_bpp2seq.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Call the function to create the .bpp2seq file
    create_bpp2seq(input_file, output_file)
