Imports Newtonsoft.Json
Imports System.Collections.Generic
Imports System.IO
Imports System.Net.Http
Imports DecoderApp.Helpers
Imports Microsoft.VisualBasic.FileIO
Imports System

Module MainModule
    Sub Main(ByVal args() As String)
        Dim testName As String = "FCA"
        Dim csvFolder As String = "C:\tmp"
        Dim byteString As String = "01CD1401018D5400064D11010645C9000BD5CC000B55C80050CD54015085D00055CDC80055490C01DA10CD009A144D00DF50CD00DF504900E454D1006450C90029D5D0002955C800EECC0C01AE504C01F3C80C0173904C0138110D01F8148500FDD01401BD4C1401C2D0D000C250940007550D018714C5004C910C014C91C400114D150191440D01D6100D0196D04401DB0C0D019B044D012051D100E048510025510901A5D450006A11D1006A0D85002F110D01EF50850074515501F4449100F90C1501B9C414013E0DD1007E094D00C314D10083504D00C8D0D400C8905400CD0C5101CD84500112110D01524C0901D7145101974C50011C0D15019C04D5002111CD006105C90066D150016685D0006BCD0C016B49D000B0D0CC0070D40801350DD100B54C5100FA50D5007A48D100FFD04C01BF504C01C4D01401448C1401C9D00C01C95048010E15CD000ED5840013D1D000D39450001891CC0018558C00DD540D019D4C050162D5CC006291C40027CD5001678C50016C110D016CD18400F10C0D01B1044D0136D1D000764D90003B110D01FB508500400DCD00400D8500054D5101C50845014A4D4D014A05C900CF0C15014FC81401D4D0CC0054148D0099D0100159D49000DED014015E8C1401230D5101A3C45001680DD10028C59400"
        Dim lenByteString As Int32 = byteString.Length
        If args.Length = 0 Then
            'Console.WriteLine("Please provide the testId and bytestring a command-line argument.")
            'Return
        Else
            testName = args(0)
            csvFolder = args(1)
        End If

        Try
            Dim byteArray As Byte() = HexStringToByteArray(byteString)
            Select Case testName
                Case "ARAT"
                    'AratDecoder(byteArray, csvPath, testId)
                Case "Motivation"
                    MDQDecoder()
                Case "PAQ"
                    'PAQDecoder(byteArray, csvPath, testId)
                Case "FCA"
                    FCADecoder(csvFolder)
                Case "BAQ"
                    BAQDecoder(byteArray)
                Case "SJT"
                    'SJTDecoder(byteArray, csvPath, testId)
                Case Else
                    Console.WriteLine("Unknown TestName: " & testName)
            End Select

        Catch ex As Exception
            Console.WriteLine("Error processing the bytestring: " & ex.Message)
        End Try

        'Console.WriteLine("Done")

    End Sub

    ' Function to convert hexadecimal string to byte array
    Private Function HexStringToByteArray(hexString As String) As Byte()
        Dim byteArray((hexString.Length \ 2) - 1) As Byte
        For i As Integer = 0 To hexString.Length - 1 Step 2
            byteArray(i \ 2) = Convert.ToByte(hexString.Substring(i, 2), 16)
        Next
        Return byteArray
    End Function

    Private Sub FCADecoder(csvFolder As String)
        ' This method takes a bytestring and returns a JSON, each containing the following items:
        '   ItemId (Integer)
        '   3 Candidate answers (Integer)
        '   All correct answers per competency that is being checked (String in which all values are separated by ", ", nonexistent values are replaced by 0
        '   TimeSpent

        ' Determine the number of items (each item is 16 bytes)
        'Dim numberOfItems As Integer = fcaAnswers.Length \ 16

        'Dim csvFolder As String = "C:\Users\miked\code\DEP2-G2\files\csv"
        Dim csvFileFCA As String = Path.Combine(csvFolder, "bytestrings_fca.csv")
        Dim csvFileDecoded As String = Path.Combine(csvFolder, "decoded_fca.csv")
        Dim csvFileFailed As String = Path.Combine(csvFolder, "failed_decodings_fca.csv")
        Console.WriteLine(csvFileFCA)
        Dim tfp As New TextFieldParser(csvFileFCA)
        tfp.Delimiters = New String() {","}
        tfp.TextFieldType = FieldType.Delimited

        Dim candidates As New List(Of Int32)
        Dim instances As New List(Of Int16)
        Dim instruments As New List(Of Int16)

        ' Fields of an itemId
        Dim itemIDs As New List(Of Int32)
        Dim answers(2) As List(Of Int16)
        Dim timeSpents As New List(Of Int32)

        ' 4 Competences
        Dim compIDs(3) As List(Of Int16)

        ' 3 answers per competence (length 4, 3)
        Dim compSeqs(3, 2) As List(Of Int16)
        Dim seqs(2) As List(Of Int16)

        For i As Integer = 0 To 2
            answers(i) = New List(Of Int16)()
            seqs(i) = New List(Of Int16)()
            For comp As Integer = 0 To 3
                compIDs(comp) = New List(Of Int16)
                compSeqs(comp, i) = New List(Of Int16)
            Next
        Next

        Using writer As New StreamWriter(csvFileDecoded, False) ' True to overwrite
            Using errorWriter As New StreamWriter(csvFileFailed, False)
                errorWriter.WriteLine(String.Join(",", "foutNr", "instanceId", "candidateId", "ex.Message"))

                ' Write headers
                Dim headers As New List(Of String)
                headers.Add("InstrumentClassId")
                headers.Add("CandidateId")
                headers.Add("InstanceId")
                headers.Add("ItemId")
                headers.Add("TimeSpent")
                For i As Int32 = 1 To 3
                    headers.Add(String.Format("Sequence{0}", i))
                    headers.Add(String.Format("Answer{0}", i))
                Next
                For j As Int32 = 1 To 4
                    headers.Add(String.Format("Competency_{0}", j))
                    For i As Int32 = 1 To 3
                        headers.Add(String.Format("Correct_answer_comp{0}_seq{1}", j, i))
                    Next
                Next
                writer.WriteLine(String.Join(",", headers))

                Dim candidateId As Integer
                Dim instanceId As Integer

                tfp.ReadLine() ' skip header
                Dim getal As Int32 = 0
                Dim fouten As Int32 = 0
                While tfp.EndOfData = False
                    getal = getal + 1
                    'Console.WriteLine(getal)
                    Try

                        Dim fields = tfp.ReadFields()
                        candidateId = fields(0)
                        instanceId = fields(1)
                        Dim instrumentClassId As Integer = fields(3)

                        Dim fcaAnswersByteArray As Byte() = HexStringToByteArray(fields(2))
                        Dim numberOfItems As Integer = fcaAnswersByteArray.Length \ 16

                        For questionIndex As Integer = 1 To numberOfItems
                            Dim helper As New BinaryFcaHelper(fcaAnswersByteArray, questionIndex)
                            'Some items have no data, so leave them out
                            If helper.ItemId <> 0 Then
                                Dim decodings As New List(Of Integer)
                                decodings.Add(instrumentClassId)
                                decodings.Add(candidateId)
                                decodings.Add(instanceId)
                                decodings.Add(helper.ItemId)
                                decodings.Add(helper.TimeSpent)
                                For i As Int32 = 1 To 3
                                    decodings.Add(helper.SequenceIds(i - 1))
                                    decodings.Add(helper.Answers(i - 1))
                                Next
                                For j As Int32 = 1 To 4
                                    Dim comp As Integer = helper.Competencies(j - 1)
                                    decodings.Add(comp)
                                    For i As Int32 = 1 To 3
                                        If comp <> 0 Then
                                            decodings.Add(helper.CorrectAnswers(String.Format("{0}_{1}", comp, helper.SequenceIds(i - 1))))
                                        Else
                                            decodings.Add(0)
                                        End If
                                    Next
                                Next
                                Dim decodedLine = String.Join(",", decodings)
                                writer.WriteLine(String.Join(",", decodings))
                            End If
                        Next

                    Catch ex As Exception
                        fouten = fouten + 1
                        errorWriter.WriteLine(String.Join(",", fouten, instanceId, candidateId, ex.Message))
                        Console.WriteLine("Caught Exception " & fouten & ": - " & instanceId & " - " & candidateId & " - " & ex.Message)
                    End Try
                End While
                Console.WriteLine("Done")
            End Using
        End Using

        Console.WriteLine($"Data has been written to {csvFileDecoded}.")
    End Sub

    Private Sub AratDecoder(ByVal ratAnswers As Byte(), ByVal csvFilePath As String, ByVal TestId As Integer)
        ' Define the assessment model configuration code (you may replace this with actual value)
        Dim assessmentModelConfigCode As String = "RAT" + TestId.ToString()

        ' Determine the number of items (each item is 16 bytes, as per your previous description)
        Dim numberOfItems As Integer = ratAnswers.Length \ 16

        Using writer As StreamWriter = New StreamWriter(csvFilePath, append:=True)
            ' Write the header only if the file is empty or being created for the first time
            If writer.BaseStream.Length = 0 Then
                writer.WriteLine("TestId,ScreenId,CloneId,ItemId,Answer,CorrectAnswer,TimeSpent,IsAnswered")
            End If
            ' Loop through each item and process it
            For questionIndex As Integer = 1 To numberOfItems
                ' Instantiate the RatHelper object with the required parameters
                Dim helper As New BinaryRatHelper(assessmentModelConfigCode, ratAnswers, questionIndex)

                writer.WriteLine($"{helper.TestId},{helper.ScreenId},{helper.CloneId},{helper.ItemId},{helper.Answer},{helper.CorrectAnswer},{helper.TimeSpent},{helper.IsAnswered}")

            Next
        End Using

    End Sub

    Private Sub SJTDecoder(ByVal sjtAnswers As Byte(), ByVal csvFilePath As String, ByVal TestId As Integer)
        ' Define the assessment model configuration code
        Dim assessmentModelConfigCode As String = "SJT" + TestId.ToString()

        ' Determine the number of items (each item is 16 bytes, as per your previous description)
        Dim numberOfItems As Integer = sjtAnswers.Length \ 16

        Using writer As StreamWriter = New StreamWriter(csvFilePath, append:=True)
            ' Write the header only if the file is empty or being created for the first time
            If writer.BaseStream.Length = 0 Then
                writer.WriteLine("TestId,SituationId,SequenceId_1,SequenceId_2,SequenceId_3,Answers_1,Answers_2,Answers_3,Scores_1,Scores_2,Scores_3,TimeSpent")
            End If
            ' Loop through each item and process it
            ' Q: Does questionIndex have to start at 1 or 0?

            For questionIndex As Integer = 1 To numberOfItems
                ' Instantiate the SJTHelper object with the required parameters
                Dim helper As New BinarySjtHelper(sjtAnswers, questionIndex)

                writer.WriteLine($"{assessmentModelConfigCode},{helper.SituationId},{String.Join(", ", helper.SequenceIds)},{String.Join(", ", helper.Answers)},{String.Join(", ", helper.Answers)},{helper.TimeSpent}")

            Next
        End Using

    End Sub

    Private Sub MDQDecoder()
        Dim csvFolder As String = "C:\Users\Lorem\OneDrive\Documenten\Hogent\1_3eJaar\Project\decoderen"
        Dim csvFileBAQ As String = Path.Combine(csvFolder, "4832881.csv")
        Dim csvFileDecoded As String = Path.Combine(csvFolder, "BAQ_decoded.csv")
        Dim csvFileFailed As String = Path.Combine(csvFolder, "BAQ_failed_decodings.csv")

        Dim tfp As New TextFieldParser(csvFileBAQ)
        tfp.Delimiters = New String() {","}
        tfp.TextFieldType = FieldType.Delimited


        ' Fields of an itemId
        Dim itemIDs As New List(Of Int32)
        Dim normatives(4) As List(Of Int16)

        Using writer As New StreamWriter(csvFileDecoded, False) ' True to overwrite
            Using errorWriter As New StreamWriter(csvFileFailed, False)
                errorWriter.WriteLine(String.Join(",", "foutNr", "instanceId", "candidateId", "ex.Message"))

                ' Write headers
                Dim headers As New List(Of String)
                headers.Add("InstrumentClassId")
                headers.Add("CandidateId")
                headers.Add("InstanceId")
                headers.Add("ItemId")
                headers.Add("TimeSpent")
                headers.Add("Answers")
                writer.WriteLine(String.Join(",", headers))

                Dim candidateId As Integer
                Dim instanceId As Integer

                tfp.ReadLine() ' skip header
                Dim getal As Int32 = 0
                Dim fouten As Int32 = 0
                While tfp.EndOfData = False
                    getal = getal + 1
                    Try

                        Dim fields = tfp.ReadFields()
                        candidateId = fields(0)
                        instanceId = fields(1)

                        Dim instrumentClassId As Integer = fields(3)

                        Dim mdqAnswersByteArray As Byte() = HexStringToByteArray(fields(2))
                        Dim numberOfItems As Integer = mdqAnswersByteArray.Length \ 8



                        For itemIndex As Integer = 1 To numberOfItems
                            Dim helper As New BinaryMdqRegulationHelper(mdqAnswersByteArray, itemIndex)
                            Console.WriteLine(helper.ItemId)
                            'Some items have no data, so leave them out
                            If helper.ItemId <> 0 Then
                                Dim decodings As New List(Of Integer)
                                decodings.Add(instrumentClassId)
                                decodings.Add(candidateId)
                                decodings.Add(instanceId)
                                decodings.Add(helper.ItemId)
                                decodings.Add(helper.NormativeValues.ToString)
                                Dim decodedLine = String.Join(",", decodings)
                                writer.WriteLine(String.Join(",", decodings))
                            End If
                        Next

                    Catch ex As Exception
                        fouten = fouten + 1
                        errorWriter.WriteLine(String.Join(",", fouten, instanceId, candidateId, ex.Message))
                        Console.WriteLine("Caught Exception " & fouten & ": - " & instanceId & " - " & candidateId & " - " & ex.Message)
                    End Try
                End While
                Console.WriteLine("Done")
            End Using
        End Using

        Console.WriteLine($"Data has been written to {csvFileDecoded}.")
    End Sub
    'Dim assessmentModelConfigCode As String = "MDQ" + TestId.ToString()
    'Dim numberOfItems As Integer = mdqAnswers.Length \ 8
    'Using writer As StreamWriter = New StreamWriter(csvFilePath, append:=True)
    '    ' Write the header only if the file is empty or being created for the first time
    '    If writer.BaseStream.Length = 0 Then
    '        writer.WriteLine("TestId,ItemId,Norm_1,Norm_2,Norm_3,Norm_4,Norm_5,Norm_6")
    '    End If
    '    ' Loop through each item and process it

    '    For itemIndex As Integer = 1 To numberOfItems
    '        Dim helper As New BinaryMdqRegulationHelper(mdqAnswers, itemIndex)

    '        writer.WriteLine($"{assessmentModelConfigCode},{helper.ItemId},{String.Join(", ", helper.NormativeValues)}")

    '    Next
    'End Using

    Private Function SortStringsByLeadingNumber(strings As List(Of String)) As List(Of String)
        ' Function that can order a list of strings given that each string starts with a number
        Return strings.OrderBy(Function(s) _
        Convert.ToInt32(New String(s.TakeWhile(Function(c) Char.IsDigit(c)).ToArray()))).ToList()
    End Function



    Private Function BAQDecoder(ByVal BAQanswers As Byte()) As String

        Dim csvFolder As String = "C:\Users\verho\Documents\School\2024-2025\Semester 1\Data Engineering Project\local files\test_csv"
        Dim csvFileBAQ As String = Path.Combine(csvFolder, "BAQ_bytestrings.csv")
        Dim csvFileDecoded As String = Path.Combine(csvFolder, "BAQ_decoded.csv")
        Dim csvFileFailed As String = Path.Combine(csvFolder, "BAQ_failed_decodings.csv")

        Dim numberOfItems As Integer = BAQanswers.Length \ 8
        Dim numberOfStatements As Integer = 1

        Dim outputList As New List(Of String)

        For questionIndex As Integer = 1 To numberOfItems
            Dim helper As New BinaryBaqHelper(BAQanswers, questionIndex, numberOfStatements)
            Dim outputLine As String = $"{helper.ItemId};"

            Dim normative As List(Of Integer) = helper.NormativeValues
            Dim ipsative As List(Of Integer) = helper.IpsativeValues
            Dim normativeString As String = ""
            Dim ipsativeString As String = ""
            For i = 0 To normative.Count - 1
                normativeString = normativeString & normative(i)
                ipsativeString = ipsativeString & ipsative(i)
                If i < normative.Count - 1 Then
                    normativeString = normativeString & ","
                    ipsativeString = ipsativeString & ","
                End If
            Next

            outputLine = outputLine & normativeString & ";" & ipsativeString

            outputList.Add(outputLine)

        Next

        Dim orderedByItemID As List(Of String) = SortStringsByLeadingNumber(outputList)

        Dim output As String = String.Join(Environment.NewLine, orderedByItemID)

        Return output


        'Dim helper As New BinaryBaqHelper(BAQanswers, 1, numberOfStatements)
        'For i = 0 To helper.NormativeValues.Count
        '    Console.WriteLine($"norm: {helper.NormativeValues(i)} - ips: {helper.IpsativeValues(i)}")
        'Next





        'Dim csvFolder As String = "C:\Users\verho\Documents\School\2024-2025\Semester 1\Data Engineering Project\local files\test_csv"
        'Dim csvFileBAQ As String = Path.Combine(csvFolder, "BAQ_bytestrings.csv")
        'Dim csvFileDecoded As String = Path.Combine(csvFolder, "BAQ_decoded.csv")
        'Dim csvFileFailed As String = Path.Combine(csvFolder, "BAQ_failed_decodings.csv")

        'Dim tfp As New TextFieldParser(csvFileBAQ)
        'tfp.Delimiters = New String() {","}
        'tfp.TextFieldType = FieldType.Delimited

        'Console.WriteLine("First few lines of the CSV file:")

        'Dim candidates As New List(Of Int32)
        'Dim instances As New List(Of Int16)
        ''Dim instruments As New List(Of Int16)

        '' Fields of an itemId
        'Dim itemIDs As New List(Of Int32)

        '' Five Ipsative values
        'Dim normativeAnswers(4) As List(Of Int32)

        '' Five normative values
        'Dim ipsativeAnswers(4) As List(Of Int32)

        'For i As Integer = 0 To 4
        '    normativeAnswers(i) = New List(Of Int32)()  ' Initialize lists for normative answers
        '    ipsativeAnswers(i) = New List(Of Int32)()   ' Initialize lists for ipsative answers
        'Next

        'Using writer As New StreamWriter(csvFileDecoded, False) ' True to overwrite
        '    Using errorWriter As New StreamWriter(csvFileFailed, False)
        '        errorWriter.WriteLine(String.Join(",", "foutNr", "instanceId", "candidateId", "ex.Message"))

        '        ' Write headers
        '        Dim headers As New List(Of String)
        '        headers.Add("CandidateId")
        '        headers.Add("InstanceId")
        '        headers.Add("ItemId")
        '        For i As Int32 = 1 To 5
        '            headers.Add("NormativeAnswer_" + Str(i))
        '            headers.Add("IpsativeAnswe_" + Str(i))
        '        Next
        '        writer.WriteLine(String.Join(",", headers))

        '        Dim candidateId As Integer
        '        Dim instanceId As Integer

        '        tfp.ReadLine() ' skip header
        '        Dim getal As Int32 = 0
        '        Dim fouten As Int32 = 0
        '        While tfp.EndOfData = False
        '            getal = getal + 1

        '            Try
        '                Dim fields = tfp.ReadFields()
        '                candidateId = fields(0)
        '                instanceId = fields(1)

        '                ' Convert the escaped hex string to a byte array
        '                Dim baqAnswersByteArray As Byte() = HexStringToByteArray(fields(2))


        '                Dim numberOfItems As Integer = baqAnswersByteArray.Length \ 8

        '                'Console.WriteLine(numberOfItems)

        '                For itemIndex As Integer = 1 To numberOfItems
        '                    Dim helper As New BinaryBaqHelper(baqAnswersByteArray, itemIndex, numberOfItems)
        '                    'Some items have no data, so leave them out



        '                    If helper.ItemId <> 0 Then
        '                        Dim decodings As New List(Of Integer)
        '                        'decodings.Add(instrumentClassId)
        '                        decodings.Add(candidateId)
        '                        decodings.Add(instanceId)
        '                        decodings.Add(helper.ItemId)
        '                        For Each value As Int32 In helper.NormativeValues
        '                            decodings.Add(value)
        '                        Next
        '                        For Each value As Int32 In helper.IpsativeValues
        '                            decodings.Add(value)
        '                        Next
        '                        'For i As Int32 = 1 To 5
        '                        '    decodings.Add(helper.NormativeValues(i))
        '                        '    decodings.Add(helper.IpsativeValues(i - 1))
        '                        'Next


        '                        Dim decodedLine = String.Join(",", decodings)
        '                        'Console.WriteLine(decodedLine)
        '                        writer.WriteLine(String.Join(",", decodings))
        '                    End If
        '                Next

        '            Catch ex As Exception
        '                fouten = fouten + 1
        '                errorWriter.WriteLine(String.Join(",", fouten, instanceId, candidateId, ex.Message))
        '                Console.WriteLine("Caught Exception " & fouten & ": - " & instanceId & " - " & candidateId & " - " & ex.Message)
        '            End Try

        '        End While


        '    End Using
        'End Using

        'Using writer As StreamWriter = New StreamWriter(csvPath, append:=True)
        '    If writer.BaseStream.Length = 0 Then
        '        writer.WriteLine("TestId,ItemId,NormativeValues,IpsativeValues")
        '    End If
        '    ' Loop through each item and process it

        '    For itemIndex As Integer = 1 To numberOfItems
        '        Dim helper As New BinaryBaqHelper(baqAnswers, itemIndex, numberOfItems)

        '        writer.WriteLine($"{assessmentModelConfigCode},{helper.ItemId},{String.Join(", ", helper.NormativeValues)},{String.Join(", ", helper.IpsativeValues)}")
        '    Next

        'End Using

    End Function

    Private Sub PAQDecoder(ByVal paqAnswers As Byte(), ByVal csvPath As String, ByVal TestId As Integer)
        Dim assessmentModelConfigCode As String = "PAQ" + TestId.ToString()

        Dim numberOfItems As Integer = paqAnswers.Length \ 12

        Using writer As StreamWriter = New StreamWriter(csvPath, append:=True)
            If writer.BaseStream.Length = 0 Then
                writer.WriteLine("TestId,CodeLeftStatement,CodeRightStatement,IsInversed,NormativeValue,Score")
            End If

            For questionIndex As Integer = 1 To numberOfItems
                Dim helper As New BinaryPaq2018Helper(paqAnswers, questionIndex)

                writer.WriteLine($"{assessmentModelConfigCode},{helper.CodeLeftStatement},{helper.CodeRightStatement},{helper.IsInversed},{helper.NormativeValue},{helper.Score}")
            Next
        End Using

    End Sub

End Module