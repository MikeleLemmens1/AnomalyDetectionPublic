Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinarySjtHelper
        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 8 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' instantiate a new SjtHelper
        ''' </summary>
        ''' <param name="sjtAnswers"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks>
        ''' The binary holds all the answers of all the items. Each item needs 16 bytes for storing its information
        ''' Index |000000000|01111111|11122222|22222333|33333334|44444444|455555...
        '''       |012345678|90123456|78901234|56789012|34567890|12345678|901234...
        '''        item 1    item 2   item 3   item 4   item 5...
        ''' 16 bytes means 128 bits and below you find the breakdown of the bits
        ''' Bitvector |00000000001111111111|2222|2222|2233|333|333|334|444|444|444|55555555556666|
        '''           |01234567890123456789|0123|4567|8901|234|567|890|123|456|789|01234567980123|
        ''' nr of Bits|20                  |4   |4   |4   |3  |3  |3  |3  |3  |3  |14
        '''           |Situation Id        |Sequence id   |Cand.Answer|Score      |Time spent
        '''                                |1    2    3   |1   2   3  |1   2   3  |
        ''' </remarks>
        Public Sub New(sjtAnswers As Byte(), questionIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            'Get the bytes for the question index
            offSet = (questionIndex - 1) * NumberOfBytes

            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = sjtAnswers(offSet + byteIndex)
            Next

            Dim bits As String = GetBinaryString(itemBytes)
            _SituationId = GetValueFromBinaryString(bits, 0, 20)
            _SequenceIds = New List(Of Integer) From {GetValueFromBinaryString(bits, 20, 4),
                                                      GetValueFromBinaryString(bits, 24, 4),
                                                      GetValueFromBinaryString(bits, 28, 4)}
            If _SequenceIds(0) = 0 Then _SequenceIds(0) = 1
            If _SequenceIds(1) = 0 Then _SequenceIds(1) = 2
            If _SequenceIds(2) = 0 Then _SequenceIds(2) = 3

            _Answers = New List(Of Integer) From {GetValueFromBinaryString(bits, 32, 3),
                                                  GetValueFromBinaryString(bits, 35, 3),
                                                  GetValueFromBinaryString(bits, 38, 3)}

            _Scores = New List(Of Integer) From {GetValueFromBinaryString(bits, 41, 3),
                                                 GetValueFromBinaryString(bits, 44, 3),
                                                 GetValueFromBinaryString(bits, 47, 3)}

            _TimeSpent = GetValueFromBinaryString(bits, 50, 14)
        End Sub
#End Region

#Region " Properties "
        Public Property SituationId As Integer
        Public Property SequenceIds As List(Of Integer)
        Public Property Answers As List(Of Integer)
        Public Property Scores As List(Of Integer)
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
                .Append(GetBinaryString(_SituationId, 20))
                .Append(GetBinaryString(_SequenceIds(0), 4))
                .Append(GetBinaryString(_SequenceIds(1), 4))
                .Append(GetBinaryString(_SequenceIds(2), 4))
                .Append(GetBinaryString(_Answers(0), 3))
                .Append(GetBinaryString(_Answers(1), 3))
                .Append(GetBinaryString(_Answers(2), 3))
                .Append(GetBinaryString(_Scores(0), 3))
                .Append(GetBinaryString(_Scores(1), 3))
                .Append(GetBinaryString(_Scores(2), 3))
                .Append(GetBinaryString(_TimeSpent, 14))
            End With

            Dim itemBytes As Byte() = GetBytesFromBinaryString(binaryBuilder.ToString)
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub
#End Region
    End Class
End Namespace