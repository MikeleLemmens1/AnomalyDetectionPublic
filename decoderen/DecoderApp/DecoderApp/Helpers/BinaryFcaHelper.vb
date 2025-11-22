Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryFcaHelper
        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 16 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' instantiate a new FcaAnswer
        ''' </summary>
        ''' <param name="fcaAnswers"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks>
        ''' The binary holds all the answers of all the items. Each item needs 16 bytes for storing its information
        ''' Index |0000000000111111|1111222222222233|3333333344444444|4455555555556666|666666...
        '''       |0123456789012345|6789012345678901|2345678901234567|8901234567890123|456789...
        '''        item 1           item 2           item 3           item 4           item 5...
        ''' 16 bytes means 128 bits and below you find the breakdown of the bits
        ''' Bitvector |                                                                                                                       11111|111|111|111|11111111111111|
        '''           |00000000001111111111|222|222|222|233|333|333|3344444444|445|555|555|5556666666|666|777|777|7777888888|888|899|999|9999900000|000|001|111|11111122222222|
        '''           |01234567890123456789|012|345|678|901|234|567|8901234567|890|123|456|7980123456|798|012|345|6798012345|678|901|234|5678901234|567|890|123|45678901234567|
        ''' nr of Bits|20                  |3  |3  |3  |3  |3  |3  |10        |3  |3  |3  |10        |3  |3  |3  |10        |3  |3  |3  |10        |3  |3  |3  |14            |
        '''           |Item Id             |Sequence id|Cand.Answer|Competency|Corr.Answer|Competency|Corr.Answer|Competency|Corr.Answer|Competency|Corr.Answer|Time spent    |
        '''                                |1   2   3  |1   2   3  |id 1      |1   2   3  |id 2      |1   2   3  |id 3      |1   2   3  |id 4      |1   2   3  |
        ''' </remarks>
        Public Sub New(fcaAnswers As Byte(), questionIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            'Get the bytes for the question index
            offSet = (questionIndex - 1) * NumberOfBytes

            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = fcaAnswers(offSet + byteIndex)
            Next

            Dim bits As String = GetBinaryString(itemBytes)
            _ItemId = GetValueFromBinaryString(bits, 0, 20)
            _SequenceIds = New List(Of Integer) From {GetValueFromBinaryString(bits, 20, 3),
                                                      GetValueFromBinaryString(bits, 23, 3),
                                                      GetValueFromBinaryString(bits, 26, 3)}
            If _SequenceIds(0) = 0 Then _SequenceIds(0) = 1
            If _SequenceIds(1) = 0 Then _SequenceIds(1) = 2
            If _SequenceIds(2) = 0 Then _SequenceIds(2) = 3

            _Answers = New List(Of Integer) From {GetValueFromBinaryString(bits, 29, 3),
                                                  GetValueFromBinaryString(bits, 32, 3),
                                                  GetValueFromBinaryString(bits, 35, 3)}

            _Competencies = New List(Of Integer) From {GetValueFromBinaryString(bits, 38, 10),
                                                       GetValueFromBinaryString(bits, 57, 10),
                                                       GetValueFromBinaryString(bits, 76, 10),
                                                       GetValueFromBinaryString(bits, 95, 10)}

            _CorrectAnswers = New Dictionary(Of String, Integer)
            If _Competencies(0) <> 0 Then
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(0), _SequenceIds(0)), GetValueFromBinaryString(bits, 48, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(0), _SequenceIds(1)), GetValueFromBinaryString(bits, 51, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(0), _SequenceIds(2)), GetValueFromBinaryString(bits, 54, 3))
            End If

            If _Competencies(1) <> 0 Then
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(1), _SequenceIds(0)), GetValueFromBinaryString(bits, 67, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(1), _SequenceIds(1)), GetValueFromBinaryString(bits, 70, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(1), _SequenceIds(2)), GetValueFromBinaryString(bits, 73, 3))
            End If

            If _Competencies(2) <> 0 Then
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(2), _SequenceIds(0)), GetValueFromBinaryString(bits, 86, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(2), _SequenceIds(1)), GetValueFromBinaryString(bits, 89, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(2), _SequenceIds(2)), GetValueFromBinaryString(bits, 92, 3))
            End If

            If _Competencies(3) <> 0 Then
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(3), _SequenceIds(0)), GetValueFromBinaryString(bits, 105, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(3), _SequenceIds(1)), GetValueFromBinaryString(bits, 108, 3))
                _CorrectAnswers.Add(String.Format("{0}_{1}", _Competencies(3), _SequenceIds(2)), GetValueFromBinaryString(bits, 111, 3))
            End If

            _TimeSpent = GetValueFromBinaryString(bits, 114, 14)
        End Sub
#End Region

#Region " Properties "
        Public Property ItemId As Integer
        Public Property SequenceIds As List(Of Integer)
        Public Property Answers As List(Of Integer)
        Public Property Competencies As List(Of Integer)
        Public Property CorrectAnswers As Dictionary(Of String, Integer)
        Public Property TimeSpent As Integer
#End Region

#Region " Methods "
#Region " Helpers "
        ''' <summary>
        ''' Get a binary representation of the value (byte array)
        ''' </summary>
        ''' <param name="bytes"></param>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Private Function GetBinaryString(bytes As Byte()) As String
            Dim binaryBuilder As New Text.StringBuilder
            bytes.ToList.ForEach(Sub(b) binaryBuilder.Append(Convert.ToString(b, 2).PadLeft(8, "0"c)))
            Return binaryBuilder.ToString
        End Function

        ''' <summary>
        ''' Get a binary representation of an integer value of the specified length
        ''' </summary>
        ''' <param name="value"></param>
        ''' <param name="length"></param>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Private Function GetBinaryString(value As Integer, length As Integer) As String
            Return Convert.ToString(value, 2).PadLeft(length, "0"c)
        End Function

        ''' <summary>
        ''' Get a byte array from a binary string
        ''' </summary>
        ''' <param name="binary"></param>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Private Function GetBytesFromBinaryString(ByVal binary As String) As Byte()
            Dim bytes As New List(Of Byte)
            For i As Integer = 0 To NumberOfBytes - 1
                bytes.Add(Convert.ToByte(binary.Substring(i * 8, 8), 2))
            Next
            Return bytes.ToArray
        End Function

        ''' <summary>
        ''' Get integer value from a set of bits
        ''' </summary>
        ''' <param name="bits"></param>
        ''' <param name="startIndex"></param>
        ''' <param name="length"></param>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Private Function GetValueFromBinaryString(bits As String, startIndex As Integer, length As Integer) As Integer
            Return Convert.ToInt32(bits.Substring(startIndex, length), 2)
        End Function
#End Region

        ''' <summary>
        ''' Update answersbinary on question index
        ''' </summary>
        ''' <param name="answersBytes"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks></remarks>
        Public Sub PutBinary(ByRef answersBytes As Byte(), questionIndex As Integer)
            Dim offSet As Integer = (questionIndex - 1) * NumberOfBytes

            Dim binaryBuilder As New Text.StringBuilder
            With binaryBuilder
                .Append(GetBinaryString(_ItemId, 20))
                .Append(GetBinaryString(_SequenceIds(0), 3))
                .Append(GetBinaryString(_SequenceIds(1), 3))
                .Append(GetBinaryString(_SequenceIds(2), 3))
                .Append(GetBinaryString(_Answers(0), 3))
                .Append(GetBinaryString(_Answers(1), 3))
                .Append(GetBinaryString(_Answers(2), 3))

                If _Competencies.Count > 0 Then
                    .Append(GetBinaryString(_Competencies(0), 10))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(0), _SequenceIds(0)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(0), _SequenceIds(1)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(0), _SequenceIds(2)), 3))
                Else
                    .Append(GetBinaryString(0, 19))
                End If

                If _Competencies.Count > 1 Then
                    .Append(GetBinaryString(_Competencies(1), 10))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(1), _SequenceIds(0)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(1), _SequenceIds(1)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(1), _SequenceIds(2)), 3))
                Else
                    .Append(GetBinaryString(0, 19))
                End If

                If _Competencies.Count > 2 Then
                    .Append(GetBinaryString(_Competencies(2), 10))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(2), _SequenceIds(0)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(2), _SequenceIds(1)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(2), _SequenceIds(2)), 3))
                Else
                    .Append(GetBinaryString(0, 19))
                End If

                If _Competencies.Count > 3 Then
                    .Append(GetBinaryString(_Competencies(3), 10))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(3), _SequenceIds(0)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(3), _SequenceIds(1)), 3))
                    .Append(GetBinaryString(GetCorrectAnswer(Competencies(3), _SequenceIds(2)), 3))
                Else
                    .Append(GetBinaryString(0, 19))
                End If

                .Append(GetBinaryString(_TimeSpent, 14))
            End With

            Dim itemBytes As Byte() = GetBytesFromBinaryString(binaryBuilder.ToString)
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub

        Function GetCorrectAnswer(competency As Integer, sequence As Integer) As Integer
            If _CorrectAnswers.ContainsKey(String.Format("{0}_{1}", competency, sequence)) Then
                Return _CorrectAnswers(String.Format("{0}_{1}", competency, sequence))
            Else
                Return 0
            End If
        End Function
#End Region
    End Class
End Namespace