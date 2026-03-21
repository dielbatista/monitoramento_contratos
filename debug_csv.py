import pandas as pd
import os

CSV_FILE = "dados.csv"

def diagnosticar():
    if not os.path.exists(CSV_FILE):
        print("❌ Erro: Arquivo não encontrado!")
        return

    print(f"✅ Arquivo encontrado: {CSV_FILE}")
    
    try:
        # Tenta ler as primeiras linhas para ver a cara do arquivo
        # Usamos sep=None para o pandas adivinhar se é , ou ;
        df = pd.read_csv(CSV_FILE, skiprows=3, encoding='latin1', sep=None, engine='python', nrows=5)
        
        print("\n--- Colunas Detectadas ---")
        print(df.columns.tolist())
        
        print("\n--- Primeiras 3 Linhas de Dados ---")
        print(df.head(3))
        
    except Exception as e:
        print(f"\n❌ Erro ao ler o arquivo: {e}")
        print("Tentando ler como Excel...")
        try:
            df_excel = pd.read_excel(CSV_FILE, skiprows=3, nrows=5)
            print("✅ Sucesso ao ler como Excel!")
            print(df_excel.columns.tolist())
        except Exception as e2:
            print(f"❌ Erro total: {e2}")

if __name__ == "__main__":
    diagnosticar()
    