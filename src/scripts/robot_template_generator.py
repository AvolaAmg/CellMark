import os
import argparse

import pandas as pd
import anndata as ad

from dosdp_template_generator import extract_gene_terms
from file_utils import read_table_to_dict

SHARED_DRIVE = "/Volumes/osumi-sutherland/development"


def extract_genes_from_anndata(anndata_path, gene_name_column, prefix, output_path):
    """
    Extracts gene names from the AnnData object and saves them to a ROBOT template.
    Params:
        anndata_path: path to the AnnData object.
        gene_name_column: column name containing the gene names.
        prefix: prefix for the gene IDs (such as ensembl or ncbigene).
        output_path: path to the output file.
    """
    if os.path.exists(anndata_path):
        anndata = ad.read_h5ad(anndata_path)
    elif os.path.exists(SHARED_DRIVE):
        anndata = ad.read_h5ad(os.path.join(SHARED_DRIVE, anndata_path))
    else:
        raise FileNotFoundError(f"File not found: {anndata_path}. Consider mounting the shared drive.")
    genes = anndata.var.index.unique().tolist()
    records = list()
    records.append(['ID', 'SC %', 'A rdfs:label', 'A oboInOwl:hasExactSynonym SPLIT=|'])
    for gene_id in genes:
        data = [prefix + ':' + gene_id, 'SO:0000704', anndata.var.loc[gene_id][gene_name_column], '']
        records.append(data)

    df = pd.DataFrame(records, columns=["ID", "TYPE", "NAME", "SYNONYMS"])
    df.to_csv(output_path, sep="\t")


def generate_genes_robot_template(input_files: list, output_filepath: str):
    used_genes = extract_gene_terms()
    gene_subset = []
    for input_file in input_files:
        records = read_table_to_dict(input_file)
        for record in records:
            if record['ID'] in used_genes:
                gene_subset.append(record)
    df = pd.DataFrame(gene_subset, columns=["ID", "TYPE", "NAME", "SYNONYMS"])
    df.to_csv(output_filepath, sep="\t")


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    subparsers = cli.add_subparsers(help="Available actions", dest="action")

    parser_generate = subparsers.add_parser("anndata", description="Anndata gene extractor")
    parser_generate.add_argument("-a", "--anndata", type=str, help="AnnData file path")
    parser_generate.add_argument("-n", "--namecolumn", type=str, help="AnnData var column name containing gene names")
    parser_generate.add_argument("-p", "--prefix", type=str, help="Gene ID prefix (such as ensembl or ncbigene)")
    parser_generate.add_argument("-o", "--out", type=str, help="Output file path")

    parser_terms = subparsers.add_parser("genes", description="Genes template extractor")
    parser_terms.add_argument("-i", "--input", action='append', type=str, help="list of input file paths")
    parser_terms.add_argument("-o", "--out", type=str, help="Output file path")

    args = cli.parse_args()

    if args.action == "anndata":
        extract_genes_from_anndata(args.anndata, args.namecolumn, args.prefix, args.out)
    elif args.action == "genes":
        generate_genes_robot_template(args.input, args.out)
    else:
        print("Invalid action: {}".format(args.action))
        exit(1)