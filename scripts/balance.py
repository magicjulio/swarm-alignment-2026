"""Print the Adaption team credit balance via the kept dummy PDF dataset (free quote, never launches extraction)."""
from dotenv import load_dotenv
from adaption import Adaption

BALANCE_DATASET_ID = "29abb22d-2e86-4f50-b2e0-9db8373daedc"

load_dotenv()
print(Adaption().datasets.get_preprocessing_credits(BALANCE_DATASET_ID).available_credits)
