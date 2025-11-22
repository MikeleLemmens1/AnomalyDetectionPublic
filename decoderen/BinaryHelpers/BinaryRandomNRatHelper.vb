Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryRandomNRatHelper
        Private screenIdBitSector As BitVector32.Section = BitVector32.CreateSection(32767)
        Private cloneIdBitSector As BitVector32.Section = BitVector32.CreateSection(32767, screenIdBitSector)

        Private itemIdBitSector As BitVector32.Section = BitVector32.CreateSection(32767)
        Private itemCloneIdBitSector As BitVector32.Section = BitVector32.CreateSection(32767, itemIdBitSector)

        Private answerBitSector As BitVector32.Section = BitVector32.CreateSection(15)
        Private correctAnswerBitSector As BitVector32.Section = BitVector32.CreateSection(15, answerBitSector)
        Private timeSpentBitSector As BitVector32.Section = BitVector32.CreateSection(4095, correctAnswerBitSector)
        Private answeredBitSector As BitVector32.Section = BitVector32.CreateSection(1, timeSpentBitSector)

        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 12 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' instantiate a new RatAnswer
        ''' </summary>
        ''' <param name="assessmentModelConfigCode"></param>
        ''' <param name="ratAnswers"></param>
        ''' <param name="questionIndex"></param>
        ''' <remarks>
        ''' The binary
        ''' Index |000000000011|111111112222|222222333333|33  
        '''       |012345678901|234567890123|456789012345|67...
        '''        item 1       item 2       item 3       item 4
        ''' Item 1 has three bit vectors each of four bytes; the first contains screen definition values : screenId (Max Value = 32767), clone id (Max Value = 32767)
        ''' The second contains item definition values:  item id (Max Value = 32767) and clone id (Max Value = 32767).
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

            Dim screenDefinition As Integer = System.BitConverter.ToInt32(itemBytes, 0)
            Dim itemDefinition As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize)
            Dim value As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize * 2)

            Dim screenDefinitionBitVector As New BitVector32(screenDefinition)
            Dim itemDefinitionBitVector As New BitVector32(itemDefinition)
            Dim valueVector As New BitVector32(value)

            _TestId = assessmentModelConfigCode
            _ScreenId = screenDefinitionBitVector(screenIdBitSector)
            _CloneId = screenDefinitionBitVector(cloneIdBitSector)

            _ItemId = itemDefinitionBitVector(itemIdBitSector)
            _ItemCloneId = itemDefinitionBitVector(itemCloneIdBitSector)

            _Answer = valueVector(answerBitSector)
            _CorrectAnswer = valueVector(correctAnswerBitSector)
            _TimeSpent = valueVector(timeSpentBitSector)
            _IsAnswered = valueVector(answeredBitSector)
        End Sub
#End Region

#Region " Properties "
        ''' <summary>
        ''' Get the question code
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property QuestionCode As String
            Get
                Return TestId & "_S" & CStr(ScreenId).PadLeft(4, "0"c) & "_C" & CStr(CloneId).PadLeft(2, "0"c) & "_Q" & CStr(ItemId).PadLeft(2, "0"c) & "_C" & CStr(ItemCloneId).PadLeft(2, "0"c)
            End Get
            Set(value As String)
                Dim details As String() = value.Split("_"c)
                Me.TestId = details(0)
                Me.ScreenId = CInt(details(1).Substring(1))
                Me.CloneId = CInt(details(2).Substring(1))
                Me.ItemId = CInt(details(3).Substring(1))
                Me.ItemCloneId = CInt(details(4).Substring(1))
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
        ''' The id of the clone of the item 
        ''' </summary>
        ''' <value></value>
        ''' <returns></returns>
        ''' <remarks></remarks>
        Public Property ItemCloneId As Integer

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

            Dim screenDefinitionBitVector As New BitVector32(0)
            screenDefinitionBitVector(screenIdBitSector) = _ScreenId
            screenDefinitionBitVector(cloneIdBitSector) = _CloneId

            Dim itemDefinitionBitVector As New BitVector32(0)
            itemDefinitionBitVector(itemIdBitSector) = _ItemId
            itemDefinitionBitVector(itemCloneIdBitSector) = _ItemCloneId

            Dim valueVector As New BitVector32(0)
            valueVector(answerBitSector) = _Answer
            valueVector(correctAnswerBitSector) = _CorrectAnswer
            valueVector(timeSpentBitSector) = _TimeSpent
            valueVector(answeredBitSector) = _IsAnswered

            Dim screenDefinitionBytes As Byte() = System.BitConverter.GetBytes(screenDefinitionBitVector.Data)
            Dim itemDefinitionBytes As Byte() = System.BitConverter.GetBytes(itemDefinitionBitVector.Data)
            Dim valueBytes As Byte() = System.BitConverter.GetBytes(valueVector.Data)

            For i As Integer = 0 To BitVectorByteSize - 1
                itemBytes(i) = screenDefinitionBytes(i)
                itemBytes(BitVectorByteSize + i) = itemDefinitionBytes(i)
                itemBytes((BitVectorByteSize * 2) + i) = valueBytes(i)
            Next

            'Update the bytes for the question index
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub
#End Region
    End Class
End Namespace