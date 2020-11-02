import bz2
import glob
import pickle
import os

from application.logic import Application

if __name__ == '__main__':
    app = Application('')
    app.database_path = 'D:\Projects\MyMusicalComposer\generation_system\database'

    # copoem = glob.glob("D:\Projects\COPOEM\Portugal\**\*.mxl", recursive=True)
    # app.parse_files(filenames=copoem, interface=None)

    # app.retrieve_database(folders=['Other'])
    # w_d, f_d = app.process_weights({}, {}, return_dicts=True)
    # app.apply_viewpoint_weights(w_d, f_d)
    # app.generate_oracle(None, line_oracle=True, line='Piano')

    # with bz2.BZ2File(app.database_path + os.sep + 'portuguese_model.pbz2', 'wb') as handle:
    #     pickle.dump(app.oracles_information['single_oracle'], handle,
    #                 protocol=pickle.HIGHEST_PROTOCOL)
    #     handle.close()
    #     print('Dumped to pickle')

    with bz2.BZ2File(app.database_path + os.sep + 'portuguese_model.pbz2', 'rb') as handle:
        unpickler = pickle.Unpickler(handle)
        data = unpickler.load()

    print('Data Loaded')
    app.oracles_information['single_oracle'] = data
    # app.generate_sequences(line_oracle=True, num_seq=1)