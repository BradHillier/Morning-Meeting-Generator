from mmg import MeetingDocumentGenerator

def main(): 
    meeting_doc = MeetingDocumentGenerator()
    meeting_doc.generate()
    meeting_doc.write_to_file()

if __name__ == '__main__':
    main()
