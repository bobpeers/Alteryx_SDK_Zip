import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
import os
import zipfile
import tarfile

class AyxPlugin:
    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        # Default properties
        self.n_tool_id: int = n_tool_id
        self.alteryx_engine: Sdk.AlteryxEngine = alteryx_engine
        self.output_anchor_mgr: Sdk.OutputAnchorManager = output_anchor_mgr

        # Custom properties
        self.SourceFieldName: str = None
        self.extract_path = None
        self.password = None
        self.no_overwrite = False
        self.files_extracted = 0
        
        self.input: IncomingInterface = None
        self.output: Sdk.OutputAnchor = None

    def pi_init(self, str_xml: str):
        # Getting the dataName data property from the Gui.html
        self.SourceFieldName = Et.fromstring(str_xml).find('SourceField').text if 'SourceField' in str_xml else None
        self.extract_path = Et.fromstring(str_xml).find('ExtractPath').text if 'ExtractPath' in str_xml else None
        self.no_overwrite = Et.fromstring(str_xml).find('NoOverwrite').text == 'True' if 'NoOverwrite' in str_xml else None
        #self.password = Et.fromstring(str_xml).find('Password').text if 'Password' in str_xml else None
        #self.password = self.alteryx_engine.decrypt_password(Et.fromstring(str_xml).find('Password').text, 0)

        # Validity checks.
        if self.SourceFieldName is None:
            self.display_error_msg('Source field cannot be empty.')
        elif self.extract_path is None or self.extract_path == '':
            self.display_error_msg('Extract path cannot be empty.')
        elif not os.path.exists(self.extract_path):
            self.display_error_msg('Extract path doesn\'t exist')


        # Getting the output anchor from Config.xml by the output connection name
        self.output = self.output_anchor_mgr.get_output_anchor('Output')

    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        self.input = IncomingInterface(self)
        return self.input

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        return True

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, 'Missing Incoming Connection.')
        return False

    def pi_close(self, b_has_errors: bool):
        self.output.assert_close()

    def display_error_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, msg_string)

    def display_info(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.info, msg_string)


class IncomingInterface:
    def __init__(self, parent: AyxPlugin):
        # Default properties
        self.parent: AyxPlugin = parent

        # Custom properties
        self.record_copier: Sdk.RecordCopier = None
        self.record_creator: Sdk.RecordCreator = None
        self.OutputField: Sdk.Field = None
        self.SourceField: Sdk.Field = None

        #output field config
        self.output_name: str = 'zip_content'
        self.output_type: Sdk.FieldType = Sdk.FieldType.string
        self.output_size: int = 1000

    def ii_init(self, record_info_in: Sdk.RecordInfo) -> bool:
        # Make sure the user provided a field to parse
        if self.parent.SourceFieldName is None:
            self.parent.display_error_msg('Select a source field')
            return False
            
        # Get information about the source path field
        self.SourceField = record_info_in.get_field_by_name(self.parent.SourceFieldName)
        #match_field_type: Sdk.FieldType = self.SourceField.type
        #match_field_size: int = self.SourceField.size

        # Returns a new, empty RecordCreator object that is identical to record_info_in.
        record_info_out = record_info_in.clone()

        # Adds field to record with specified name and output type.
        self.OutputField = record_info_out.add_field(self.output_name, self.output_type, self.output_size)

        # Lets the downstream tools know what the outgoing record metadata will look like
        self.parent.output.init(record_info_out)

        # Creating a new, empty record creator based on record_info_out's record layout.
        self.record_creator = record_info_out.construct_record_creator()

        # Instantiate a new instance of the RecordCopier class.
        self.record_copier = Sdk.RecordCopier(record_info_out, record_info_in)

        # Map each column of the input to where we want in the output.
        for index in range(record_info_in.num_fields):
            # Adding a field index mapping.
            self.record_copier.add(index, index)

        # Let record copier know that all field mappings have been added.
        self.record_copier.done_adding()

        return True
        '''
            def unzip(self, file, path, no_overwrite, password=None):
                files = []
                file = file.lower()
                if file.endswith('tar.gz'):
                    z = tarfile.open(file,'r:gz')
                    listOfFileNames = z.getnames()
                elif file.endswith('tar'):
                    z = tarfile.open(file, 'r:')
                    listOfFileNames = z.getnames()
                elif file.endswith('zip'):
                    z = zipfile.ZipFile(file, 'r')
                    listOfFileNames = z.namelist()

                for fileName in listOfFileNames:
                    dest = os.path.join(path, fileName)
                    if os.path.exists(dest) and no_overwrite:         
                        self.parent.display_info(f'{dest} already exists and will not be overwritten')
                    else:
                        z.extract(fileName, path)
                        files.append(dest)
                        self.parent.files_extracted += 1
                z.close()
                return files
        '''
    def unzip(self, file, path, no_overwrite, password=None):
        files = []
        extension = os.path.splitext(file)[1].lower()
        ext_type = {'.zip':'r', '.tar':'r:', '.gz':'r:gz'}
        open_mode = ext_type[extension]
        
        if extension == '.zip':
            z = zipfile.ZipFile(file, open_mode)
            listOfFileNames = z.namelist()
        else:
            z = tarfile.open(file, open_mode)
            listOfFileNames = z.getnames()

        for fileName in listOfFileNames:
            dest = os.path.join(path, fileName)
            if os.path.exists(dest) and no_overwrite:         
                self.parent.display_info(f'{dest} already exists and will not be overwritten')
            else:
                z.extract(fileName, path)
                files.append(dest)
                self.parent.files_extracted += 1
        z.close()
        return files

    def ii_push_record(self, in_record: Sdk.RecordRef) -> bool:
        # Copy the data from the incoming record into the outgoing record.
        self.record_creator.reset()
        self.record_copier.copy(self.record_creator, in_record)

        # Get the text to parse and set the matches counter
        source: str = self.SourceField.get_as_string(in_record)

        output_str: str = ''
        failed_op: bool = False

        # make all dirs in path if selected
        #if self.parent.create_dirs:
        #    try:
        #        os.makedirs(os.path.dirname(dest), exist_ok=True)
        #    except OSError as e:
        #        self.parent.display_error_msg("Unable to create directory tree")

        # Check if value is null
        if source is not None and self.parent.extract_path is not None:
            try:
                if not os.path.exists(source):
                    self.parent.display_error_msg('Source file doesn\'t exist')
                elif not os.path.exists(self.parent.extract_path):
                    self.parent.display_error_msg('Extract path doesn\'t exist')
                else:
                    if source.lower().endswith(('zip', 'tar', 'tar.gz')):
                        files = self.unzip(source, self.parent.extract_path, self.parent.no_overwrite, self.parent.password)
                        for file in files:
                            self.OutputField.set_from_string(self.record_creator, file)
                            out_record = self.record_creator.finalize_record()
                            self.parent.output.push_record(out_record)

            except (IOError, os.error) as e:
                    failed_op = True
                    output_str = str(e)
                    self.OutputField.set_from_string(self.record_creator, output_str)
                    out_record = self.record_creator.finalize_record()
                    self.parent.output.push_record(out_record)
        return True

    def ii_update_progress(self, d_percent: float):
        # Inform the Alteryx engine of the tool's progress.
        self.parent.alteryx_engine.output_tool_progress(self.parent.n_tool_id, d_percent)

        # Inform the outgoing connections of the tool's progress.
        self.parent.output.update_progress(d_percent)

    def ii_close(self):
        self.parent.display_info(f'Extracted {self.parent.files_extracted} files')
        # Close outgoing connections.
        self.parent.output.close()
