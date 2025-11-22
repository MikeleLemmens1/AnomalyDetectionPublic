Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryPaq2018Helper

        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 12 'Defined in old CSO version as the number of bytes reserved for one item, 2 bitvectors => 64 bits => 8 bytes
        Private Const CharSimplifyOffset As Integer = 64 'Decimal value for first possible character. In our case A is the first possible character. The decimal value of A is 65 so we subtract 64.

        Private nonNumeric1BitSector As BitVector32.Section = BitVector32.CreateSection(31)
        Private nonNumeric2BitSector As BitVector32.Section = BitVector32.CreateSection(31, nonNumeric1BitSector)
        Private nonNumeric3BitSector As BitVector32.Section = BitVector32.CreateSection(31, nonNumeric2BitSector)
        Private numericBitSector As BitVector32.Section = BitVector32.CreateSection(127, nonNumeric3BitSector)
        Private nonNumeric1BitSectorPart2 As BitVector32.Section = BitVector32.CreateSection(31, numericBitSector)
        Private inversedBitSector As BitVector32.Section = BitVector32.CreateSection(1)
        Private answerBitSector As BitVector32.Section = BitVector32.CreateSection(7, inversedBitSector)

#Region " Properties "

        Public Property CodeLeftStatement As String
        Public Property CodeRightStatement As String
        Public Property IsInversed As Boolean
        Public Property NormativeValue As Nullable(Of Integer)
        Public ReadOnly Property Score As Integer
            Get
                If NormativeValue.HasValue Then
                    Return If(IsInversed, 6 - NormativeValue.Value, NormativeValue.Value)
                End If
                Return 0
            End Get
        End Property
#End Region

#Region " Constructors "
        ''' <summary>
        ''' Instantiate a new BinaryPaq2018Helper
        ''' </summary>
        ''' <param name="paq2018Answers"></param>
        ''' <param name="itemIndex">config index - 1 / 5</param>
        ''' <remarks>
        ''' 
        ''' -> EXAMPLE 
        ''' - left statement: EMO_15
        ''' - right statement: EMO_25
        ''' - answer: 3
        ''' - isInversed: 1
        ''' - version v1.0
        '''                 25-7
        ''' The first bitvector is divided in the following sections
        ''' - 5 * 5 bits for the facet characters of left statement
        '''     -> example: EMO = 5th letter of abc, 13th letter of abc, 15th letter of abc
        '''     -> 00101|10010|10100|00000|00000 
        ''' -  bits for the facetnr (max. 127 per facet) of left statement
        '''     -> 0001111
        ''' The second bitvector is divided in the following sections
        ''' - 5 * 5 bits for the facet characters of left statement
        '''     -> example: EMO = 5th letter of abc, 13th letter of abc, 15th letter of abc
        '''     -> 00101|10010|10100|00000|00000 
        ''' - 7 bits for the facetnr (max. 127 per facet) of left statement
        '''     -> 0011001
        ''' The third bitvector is divided 
        ''' - 1 bit for isInversed yes or no (1 or 0)
        ''' - 3 bits for answer value (1 to 5)
        '''     -> 011
        ''' Result is 3 bitvectors looking like 
        '''     00101100101010000000000000001111
        '''     00101100101010000000000000011001
        '''     01110000000000000000000000000000
        ''' </remarks>
        Public Sub New(paq2018Answers As Byte(), itemIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            offSet = CInt(itemIndex - 1) * NumberOfBytes
            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = paq2018Answers(offSet + byteIndex)
            Next

            Dim leftStatement As Integer = System.BitConverter.ToInt32(itemBytes, 0)
            Dim rightStatement As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize)
            Dim value As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize * 2)

            Dim leftStatementBitVector As New BitVector32(leftStatement)
            Dim rightStatementBitVector As New BitVector32(rightStatement)
            Dim valueBitVector As New BitVector32(value)

            _CodeLeftStatement = GetStatementFromVector(leftStatementBitVector)
            _CodeRightStatement = GetStatementFromVector(rightStatementBitVector)

            _IsInversed = CBool(valueBitVector(inversedBitSector))
            _NormativeValue = valueBitVector(answerBitSector)

        End Sub

        ''' <summary>
        ''' Create non numeric part of code
        ''' </summary>
        ''' <param name="parts"></param>
        ''' <returns></returns>
        Private Function CreateNonNumericCodePart(parts As List(Of Char)) As String
            Return New String(parts.ToArray)
        End Function

        ''' <summary>
        ''' Convert integer to character
        ''' </summary>
        ''' <param name="numericValue"></param>
        ''' <returns></returns>
        Private Function ConvertToChar(numericValue As Integer) As Char
            Return Chr(numericValue + CharSimplifyOffset)
        End Function

        ''' <summary>
        ''' Convert char to integer
        ''' </summary>
        ''' <param name="character"></param>
        ''' <returns></returns>
        Private Function ConvertToInt(character As Char) As Integer
            Return Asc(character) - CharSimplifyOffset
        End Function
#End Region

#Region " Methods "
        ''' <summary>
        ''' Update answersbinary on question index
        ''' </summary>
        ''' <param name="answerBytes"></param>
        ''' <param name="itemIndex"></param>
        ''' <remarks></remarks>
        Public Sub PutBinary(ByRef answerBytes As Byte(), itemIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            offSet = CInt(itemIndex - 1) * NumberOfBytes

            Dim leftStatementBitVector As BitVector32 = GetVectorFromStatement(CodeLeftStatement)
            Dim rightStatementBitVector As BitVector32 = GetVectorFromStatement(CodeRightStatement)

            Dim valueBitVector As New BitVector32(0)
            valueBitVector(inversedBitSector) = CInt(IsInversed)
            valueBitVector(answerBitSector) = If(NormativeValue.HasValue, NormativeValue.Value, 0)

            Dim leftStatementBytes As Byte() = System.BitConverter.GetBytes(leftStatementBitVector.Data)
            Dim rightStatementBytes As Byte() = System.BitConverter.GetBytes(rightStatementBitVector.Data)
            Dim valueBytes As Byte() = System.BitConverter.GetBytes(valueBitVector.Data)

            For index As Integer = 0 To BitVectorByteSize - 1
                itemBytes(index) = leftStatementBytes(index)
                itemBytes(BitVectorByteSize + index) = rightStatementBytes(index)
                itemBytes((BitVectorByteSize * 2) + index) = valueBytes(index)
            Next

            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answerBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub

        Private Function GetVectorFromStatement(ByVal statement As String) As BitVector32
            Dim statementBitvector As New BitVector32(0)
            Dim statementChars = statement.Split("_"c)(0).ToList.Select(Function(c) ConvertToInt(c)).ToList
            statementBitvector(nonNumeric1BitSector) = statementChars(0)
            statementBitvector(nonNumeric2BitSector) = statementChars(1)
            statementBitvector(nonNumeric3BitSector) = statementChars(2)
            statementBitvector(numericBitSector) = CInt(statement.Split("_"c)(1))

            If statement.Length > 6 Then
                statementChars = statement.Split("_"c)(2).ToList.Select(Function(c) ConvertToInt(c)).ToList
                statementBitvector(nonNumeric1BitSectorPart2) = statementChars(0)
            End If

            Return statementBitvector
        End Function

        Public Function GetStatementFromVector(ByVal bitvector As BitVector32) As String
            Dim characters As New List(Of Char) From {
            ConvertToChar(bitvector(nonNumeric1BitSector)),
            ConvertToChar(bitvector(nonNumeric2BitSector)),
            ConvertToChar(bitvector(nonNumeric3BitSector))
            }

            Dim nonNumericCodePart As String, numericCodePart As Integer
            nonNumericCodePart = CreateNonNumericCodePart(characters)
            numericCodePart = bitvector(numericBitSector)

            If bitvector(nonNumeric1BitSectorPart2) <> 0 Then
                Dim characters2 As New List(Of Char) From {
                ConvertToChar(bitvector(nonNumeric1BitSectorPart2))
                }
                Dim nonNumericCodePart2 As String
                nonNumericCodePart2 = CreateNonNumericCodePart(characters2)

                Return $"{nonNumericCodePart}_{numericCodePart.ToString().PadLeft(2, "0"c)}_{nonNumericCodePart2}"
            Else
                Return $"{nonNumericCodePart}_{numericCodePart.ToString().PadLeft(2, "0"c)}"
            End If
        End Function
#End Region

    End Class
End Namespace
