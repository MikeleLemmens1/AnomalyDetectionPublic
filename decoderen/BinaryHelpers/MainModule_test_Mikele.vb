Imports System
Imports System.Collections.Generic
Imports System.IO
Imports DecoderApp.Helpers
Imports Newtonsoft.Json

Module MainModule
    Sub Main(ByVal args() As String)

        If args.Length = 0 Then
            Console.WriteLine("Please provide the testId and bytestring a command-line argument.")
            Return
        End If
        Dim testName As String = args(0)
        'Dim testId As Integer = args(1)
        Dim byteString As String = args(1)
        ' Dim csvPath As String = args(3)

        Try
            Dim byteArray As Byte() = HexStringToByteArray(byteString)
            Select Case testName
                Case "ARAT"
                    'AratDecoder(byteArray, csvPath, testId)
                Case "Motivation"
                    'MDQDecoder(byteArray, csvPath, testId)
                Case "PAQ"
                    'PAQDecoder(byteArray, csvPath, testId)
                Case "FCA"
                    FCADecoder(byteArray)
                Case "BAQ"
                    'BAQDecoder(byteArray, csvPath, testId)
                Case "SJT"
                    'SJTDecoder(byteArray, csvPath, testId)
                Case Else
                    Console.WriteLine("Unknown TestName: " & testName)
            End Select

        Catch ex As Exception
            ' Console.WriteLine("Error processing the bytestring: " & ex.Message)
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

    Private Sub FCADecoder(ByVal fcaAnswers As Byte())
        ' This method takes a bytestring and returns a JSON, each containing the following items:
        '   ItemId (Integer)
        '   3 Candidate answers (Integer)
        '   All correct answers per competency that is being checked (String in which all values are separated by ", ", nonexistent values are replaced by 0
        '   TimeSpent

        ' Determine the number of items (each item is 16 bytes)
        Dim numberOfItems As Integer = fcaAnswers.Length \ 16

        ' Output result as JSON
        Dim jsonDataList As New List(Of Dictionary(Of String, Object))

        For questionIndex As Integer = 1 To numberOfItems
            Dim jsonData As New Dictionary(Of String, Object)
            Dim helper As New BinaryFcaHelper(fcaAnswers, questionIndex)

            ' I think CorrectAnswers is a dict made of keys made like this: "CompId(0)_SeqId(0)", with com ranging from 10 to 13 and seq from 1 to 3
            ' When I call the dictionary with a non-existing key, the script fails, so I fill the dict with zeros where the key is missing
            ' I believe a set of 3 answers has several combinations of correct answers, depending on the sequence and competence to be checked

            Dim Competencies As New List(Of String) From {"10", "11", "12", "13"} 'I hope the keys are actually in this range
            Dim SequenceIds As New List(Of String) From {"1", "2", "3"}

            For Each competency As String In Competencies
                For Each sequenceId As String In SequenceIds
                    Dim key As String = competency & "_" & sequenceId
                    Dim value As String
                    ' Check if the key exists in the dictionary, write 0 if not present
                    If helper.CorrectAnswers.ContainsKey(key) Then
                        value = helper.CorrectAnswers(key)
                    Else
                        helper.CorrectAnswers.Add(key, 0)
                    End If
                Next
            Next

            'Concatenate the answers to be able to write them in a csv (easier than calling all of them separately), remove the last ", "
            Dim correctAnswers As String = ""

            For Each key As String In helper.CorrectAnswers.Keys
                correctAnswers = correctAnswers & helper.CorrectAnswers(key) & ", "
            Next
            correctAnswers = correctAnswers.Substring(0, correctAnswers.Length - 2)

            'Some items have no data, so leave them out
            If helper.ItemId <> 0 Then
                'Create a JSON
                jsonData("ItemId") = helper.ItemId
                jsonData("Answer1") = helper.Answers(0)
                jsonData("Answer2") = helper.Answers(1)
                jsonData("Answer3") = helper.Answers(2)
                jsonData("CorrectAnswers") = correctAnswers
                jsonData("TimeSpent") = helper.TimeSpent
                jsonDataList.Add(jsonData)

            End If

        Next
        Dim jsonOutput As String = JsonConvert.SerializeObject(jsonDataList, Formatting.Indented)
        Console.WriteLine(jsonOutput)
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

    Private Sub MDQDecoder(ByVal mdqAnswers As Byte(), ByVal csvFilePath As String, ByVal TestId As Integer)
        Dim assessmentModelConfigCode As String = "MDQ" + TestId.ToString()
        Dim numberOfItems As Integer = mdqAnswers.Length \ 8
        Using writer As StreamWriter = New StreamWriter(csvFilePath, append:=True)
            ' Write the header only if the file is empty or being created for the first time
            If writer.BaseStream.Length = 0 Then
                writer.WriteLine("TestId,ItemId,Norm_1,Norm_2,Norm_3,Norm_4,Norm_5,Norm_6")
            End If
            ' Loop through each item and process it

            For itemIndex As Integer = 1 To numberOfItems
                Dim helper As New BinaryMdqRegulationHelper(mdqAnswers, itemIndex)

                writer.WriteLine($"{assessmentModelConfigCode},{helper.ItemId},{String.Join(", ", helper.NormativeValues)}")

            Next
        End Using
    End Sub
    Private Sub BAQDecoder(ByVal baqAnswers As Byte(), ByVal csvPath As String, ByVal TestId As Integer)
        Dim assessmentModelConfigCode As String = "BAQ" + TestId.ToString()

        Dim numberOfItems As Integer = baqAnswers.Length / 8

        Using writer As StreamWriter = New StreamWriter(csvPath, append:=True)
            If writer.BaseStream.Length = 0 Then
                writer.WriteLine("TestId,ItemId,NormativeValues,IpsativeValues")
            End If
            ' Loop through each item and process it

            For itemIndex As Integer = 1 To numberOfItems
                Dim helper As New BinaryBaqHelper(baqAnswers, itemIndex, numberOfItems)

                writer.WriteLine($"{assessmentModelConfigCode},{helper.ItemId},{String.Join(", ", helper.NormativeValues)},{String.Join(", ", helper.IpsativeValues)}")
            Next

        End Using

    End Sub

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
