from utils.main import main
import traceback

try:
    main()
except:
    traceback.print_exc()