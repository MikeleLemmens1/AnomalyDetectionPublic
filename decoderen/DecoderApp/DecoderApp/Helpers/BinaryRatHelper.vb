Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryRatHelper
        Private screenIdBitSector As BitVector32.Section = BitVector32.CreateSection(32767)
        Private cloneIdBitSector As BitVector32.Section = BitVector32.CreateSection(255, screenIdBitSector)
        Private itemIdBitSector As BitVector32.Section = BitVector32.CreateSection(255, cloneIdBitSector)

        Private answerBitSector As BitVector32.Section = BitVector32.CreateSection(15)
        Private correctAnswerBitSector As BitVector32.Section = BitVector32.CreateSection(15, answerBitSector)
        Private timeSpentBitSector As BitVector32.Section = BitVector32.CreateSection(4095, correctAnswerBitSector)
        Private answeredBitSector As BitVector32.Section = BitVector32.CreateSection(1, timeSpentBitSector)

        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 8 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' instantiate a new RatAnswer
        ''' </summary>
        ''' <param name="assessmentModelConfigCode"></param>
        ''' <param name="ratAnswers"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks>
        ''' The binary
        ''' Index |00000000|00111111|11112222|22222233|333333  
        '''       |01234567|89012345|67890123|45678901|234656...
        '''        item 1   item 2   item 3   item 4   item 5
        ''' Item 1 has two bit vectors each of four bytes; the first contains definition values : screenId (Section : 32767 long), clone id (255 long), item id (255 long).
        ''' The second bit vectors holds : answer of the candidate (15 long), correct answer (15 long), timespent (4095 long), answered (1 long)
        ''' </remarks>
        Public Sub New(ByVal assessmentModelConfigCode As String, ratAnswers As Byte(), questionIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            'Get the bytes for the question index
            offSet = (questionIndex - 1) * NumberOfBytes
            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = ratAnswers(offSet + byteIndex)
            Next

            Dim definition As Integer = System.BitConverter.ToInt32(itemBytes, 0)
            Dim value As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize)

            Dim definitionBitVector As New BitVector32(definition)
            Dim valueVector As New BitVector32(value)

            _TestId = assessmentModelConfigCode
            _ScreenId = definitionBitVector(screenIdBitSector)
            _CloneId = definitionBitVector(cloneIdBitSector)
            _ItemId = definitionBitVector(itemIdBitSector)

            _Answer = valueVector(answerBitSector)
            _CorrectAnswer = valueVector(correctAnswerBitSector)
            _TimeSpent = valueVector(timeSpentBitSector)
            _IsAnswered = valueVector(answeredBitSector)
        End Sub
#End Region

#Region " Properties "
        Public Property QuestionCode As String
            Get
                Return _TestId & "_S" & CStr(ScreenId).PadLeft(4, "0"c) & "_C" & CStr(CloneId).PadLeft(2, "0"c) & "_Q" & CStr(ItemId).PadLeft(2, "0"c)
            End Get
            Set(value As String)
                Dim details As String() = value.Split("_"c)
                Me._TestId = details(0)
                Me.ScreenId = CInt(details(1).Substring(1))
                Me.CloneId = CInt(details(2).Substring(1))
                Me.ItemId = CInt(details(3).Substring(1))
            End Set
        End Property

        ''' <summary>
        ''' The id of the test. Or the first part of the question code.
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property TestId As String

        ''' <summary>
        ''' The id of the screen; the second part of the question code.
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property ScreenId As Integer

        ''' <summary>
        ''' The id of the clone; the third part of the question code
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property CloneId As Integer

        ''' <summary>
        ''' The id of the question; the last part of the question code
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property ItemId As Integer

        ''' <summary>
        ''' The answer given by the candidate for this item
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property Answer As Integer

        ''' <summary>
        ''' The correct answer of the item
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property CorrectAnswer As Integer

        ''' <summary>
        ''' The number of seconds the candidate spent on the item
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property TimeSpent As Integer

        ''' <summary>
        ''' Is the item answered?
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property IsAnswered As Integer

        ''' <summary>
        ''' Is the item empty or not?
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public ReadOnly Property IsEmpty As Boolean
            Get
                Return ItemId.Equals(0)
            End Get
        End Property
#End Region

#Region " Methods "
        ''' <summary>
        ''' Update answersbinary on question index
        ''' </summary>
        ''' <param name="answersBytes"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks></remarks>
        Public Sub PutBinary(ByRef answersBytes As Byte(), questionIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte '8 bytes

            'Get the bytes for the question index
            offSet = (questionIndex - 1) * NumberOfBytes

            Dim definitionBitVector As New BitVector32(0)
            definitionBitVector(screenIdBitSector) = _ScreenId
            definitionBitVector(cloneIdBitSector) = _CloneId
            definitionBitVector(itemIdBitSector) = _ItemId

            Dim valueVector As New BitVector32(0)
            valueVector(answerBitSector) = _Answer
            valueVector(correctAnswerBitSector) = _CorrectAnswer
            valueVector(timeSpentBitSector) = _TimeSpent
            valueVector(answeredBitSector) = _IsAnswered

            Dim definitionBytes As Byte() = System.BitConverter.GetBytes(definitionBitVector.Data)
            Dim valueBytes As Byte() = System.BitConverter.GetBytes(valueVector.Data)

            For i As Integer = 0 To BitVectorByteSize - 1
                itemBytes(i) = definitionBytes(i)
                itemBytes(BitVectorByteSize + i) = valueBytes(i)
            Next

            'Update the bytes for the question index
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub
#End Region
    End Class
End Namespace